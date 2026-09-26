import asyncio
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from logging.handlers import QueueListener
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from cron.setup_jobs import setup_jobs, scheduler
from database.engine import get_session
from filas.file_setup import file_setup
from repositories.JobRepository import CronRepository
from routes.web import add_web_routes
from routes.api import add_api_routes
from services.OpenWebuiSocketClient import owui_socket, socket_habilitado
import sys
import os
from threading import Event
import dotenv
from libraries.logger.log import CustomLogger

logger = CustomLogger.get_logger(__name__)

env_file = None
if "--env-file" in sys.argv:
    idx = sys.argv.index("--env-file")
    if idx + 1 < len(sys.argv):
        env_file = sys.argv[idx + 1]

if env_file:
    dotenv.load_dotenv(env_file, override=True)
else:
    dotenv.load_dotenv(override=True)

CRON_ENABLED = os.getenv("CRON_ENABLED", "False").lower() in ("true", "1", "yes")

_APP_LOG_LISTENER: QueueListener | None = None


def _run_migrations() -> None:
    """Executa as migrations do Alembic programaticamente antes de iniciar a aplicação."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Migration do banco principal
    try:
        alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "database", "migrations"))
        alembic_command.upgrade(alembic_cfg, "head")
        logger.info("✅ Migrations do banco principal aplicadas com sucesso")
    except Exception as e:
        logger.error("❌ Erro ao aplicar migrations do banco principal: %s", e)
        raise RuntimeError("Falha ao aplicar migrations do banco principal") from e

    # Migration do banco indexador
    try:
        alembic_index_cfg = AlembicConfig(os.path.join(base_dir, "alembic_index.ini"))
        alembic_index_cfg.set_main_option("script_location", os.path.join(base_dir, "database", "migrations_index"))
        alembic_command.upgrade(alembic_index_cfg, "head")
        logger.info("✅ Migrations do banco indexador aplicadas com sucesso")
    except Exception as e:
        logger.error("❌ Erro ao aplicar migrations do banco indexador: %s", e)
        raise RuntimeError("Falha ao aplicar migrations do banco indexador") from e


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação (startup/shutdown)."""
    # _run_migrations()

    fila_task = None
    fila_stop_event = Event()
    setup_timeout_seconds = 20

    try:
        # 1) Jobs: com timeout — NUNCA bloqueia o yield da API
        print("STARTUP: setup_jobs...", flush=True)
        try:
            await asyncio.wait_for(
                asyncio.to_thread(setup_jobs, include_acervo=CRON_ENABLED),
                timeout=setup_timeout_seconds,
            )
            print("STARTUP: setup_jobs OK", flush=True)
        except asyncio.TimeoutError:
            logger.error(
                "❌ setup_jobs excedeu %ss (possível lock no banco). Seguindo sem jobs.",
                setup_timeout_seconds,
            )
            print(
                f"STARTUP: setup_jobs TIMEOUT ({setup_timeout_seconds}s) — API sobe sem jobs",
                flush=True,
            )
        except Exception as e:
            logger.error("❌ Erro em setup_jobs (seguindo sem jobs): %s", e)
            print(f"STARTUP: setup_jobs FALHOU: {e}", flush=True)

        # 2) Scheduler (sessão curta — fecha em seguida; com timeout)
        if not scheduler.running:
            print("STARTUP: iniciando scheduler...", flush=True)

            def _start_scheduler() -> None:
                session_gen = get_session()
                try:
                    session = next(session_gen)
                    cron_repository = CronRepository(session)
                    crons = cron_repository.find_all()
                    scheduler.start()
                    jobs = [job.id for job in scheduler.get_jobs()]

                    for job_id in jobs:
                        cron = next((cron for cron in crons if cron.id == job_id), None)
                        should_pause_job_due_to_enabled_cron = CRON_ENABLED and cron and not cron.active
                        should_pause_job_due_to_disabled_cron = not CRON_ENABLED and (
                            not cron or not cron.active
                        )

                        if should_pause_job_due_to_enabled_cron or should_pause_job_due_to_disabled_cron:
                            scheduler.pause_job(job_id)
                finally:
                    try:
                        session_gen.close()
                    except Exception:
                        pass

            try:
                await asyncio.wait_for(
                    asyncio.to_thread(_start_scheduler),
                    timeout=setup_timeout_seconds,
                )
                logger.info("✅ Scheduler iniciado com sucesso")
                print("STARTUP: scheduler OK", flush=True)
            except asyncio.TimeoutError:
                logger.error(
                    "❌ Scheduler excedeu %ss. Seguindo sem scheduler.",
                    setup_timeout_seconds,
                )
                print(
                    f"STARTUP: scheduler TIMEOUT ({setup_timeout_seconds}s)",
                    flush=True,
                )
            except Exception as e:
                logger.error("❌ Erro ao iniciar scheduler (seguindo sem scheduler): %s", e)
                print(f"STARTUP: scheduler FALHOU: {e}", flush=True)
        # 3) Socket do Open WebUI (stream do chat com subagentes)
        if socket_habilitado():
            print("STARTUP: conectando socket do Open WebUI...", flush=True)
            owui_socket.iniciar()

        # 4) Fila + libera a API
        print("STARTUP: iniciando fila...", flush=True)
        fila_task = asyncio.create_task(file_setup(fila_stop_event))
        print("STARTUP: Application startup complete", flush=True)
        yield
    finally:
        await owui_socket.parar()
        fila_stop_event.set()
        if fila_task:
            fila_task.cancel()
            try:
                await fila_task
            except asyncio.CancelledError:
                pass
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("✅ Scheduler parado com sucesso")


class CustomFastAPI(FastAPI):
    #
    def openapi(self):
        openapi_schema = super().openapi()
        if "paths" in openapi_schema:
            sorted_paths = sorted(
                openapi_schema["paths"].items(),
                key=lambda item: (
                    next(
                        (
                            (method_info.get("tags", [""])[0].lower())
                            for method_info in item[1].values()
                            if "tags" in method_info and method_info["tags"]
                        ),
                        "",
                    ),
                    item[0],
                ),
            )
            openapi_schema["paths"] = dict(sorted_paths)
        if "tags" in openapi_schema:
            openapi_schema["tags"] = sorted(openapi_schema["tags"], key=lambda t: t.get("name", "").lower())
        return openapi_schema


app = CustomFastAPI(
    title="PGM Connect",
    version="1.0.0",
    description="PGM Connect",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "docExpansion": "none",
        "syntaxHighlight": {"theme": "obsidian"},
    },
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")


# Configs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

add_web_routes(app)
add_api_routes(app)


# Exception handler global para erros de validação do Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler customizado para erros de validação com detalhes mais legíveis"""
    campos = []
    for erro in exc.errors():
        campo = ".".join(str(x) for x in erro["loc"][1:])  # Remove "body" do início
        campos.append(
            {
                "campo": campo,
                "tipo": erro["type"],
                "mensagem": erro["msg"],
                "valor_recebido": erro.get("input"),
                "localizacao": list(erro["loc"]),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "status": "erro",
            "mensagem": "Validação de dados falhou",
            "detalhes": f"Foram encontrados {len(campos)} erro(s) na validação",
            "campos": campos,
            "codigo_erro": "VALIDATION_ERROR",
            "rota": str(request.url.path),
            "metodo": request.method,
        },
    )


# Handler global para exceções não tratadas (evita status 0 / Unknown Error no cliente)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Garante que toda exceção não tratada retorne uma resposta JSON, evitando conexão fechada (status 0)."""
    logger.exception("Exceção não tratada: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": "erro",
            "mensagem": "Erro interno do servidor",
            "codigo_erro": "INTERNAL_SERVER_ERROR",
            "rota": str(request.url.path),
            "metodo": request.method,
        },
    )
