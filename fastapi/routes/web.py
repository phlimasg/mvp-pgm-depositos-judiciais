from controllers.AcervoController import acervo_router
from controllers.AtaController import atas_router, atas_public_router
from controllers.MidiaIndoorController import midia_indoor_router, midia_indoor_public_router
from controllers.AuthController import auth_router, fast_auth_router
from controllers.AutoJudicialController import auto_judicial_router
from controllers.BCadastroController import bcadastro_router
from controllers.CronController import cron_router
from controllers.TJRJController import tjrj_router
from controllers.AuthPerfilController import perfil_router
from controllers.AuthRegraController import regra_router
from controllers.BucketController import bucket_router
from controllers.DevTools import dev_tools_router
from controllers.health_controller import health_router
from controllers.HonorariosApuracaoController import apuracao_router
from controllers.HonorariosAfastamentosController import honorarios_afastamentos_router
from controllers.PageController import router as page_router
from controllers.AuthAplicacaoController import aplicacao_router
from controllers.HonorariosUploadPlanilhaController import upload_router
from controllers.FuncionariosController import funcionarios_router
from controllers.CargoController import cargos_router
from controllers.SetorController import setores_router
from controllers.RoleController import role_router
from controllers.AcessosController import acessos_router
from controllers.CargaInicial import carga_inicial
from controllers.HonorariosController import honorarios_router, honorarios_contadoria_router
from controllers.HonorariosAgrupamentoFuncionarioController import honorarios_agrupamento_router
from controllers.AcolhimentoController import acolhimento_router
from controllers.WebSocketController import websocket_router
from controllers.NotificacaoController import router_notificacoes
from controllers.ReportController import report_router
from controllers.CursosController import cursos_router
from controllers.LogsController import logs_router
from controllers.ChaveAPIController import chave_api_router
from fastapi import Depends, FastAPI
from fastapi.routing import APIRouter
from libraries.env import env
from middlewares.auth_middleware import auth_middleware
from controllers.PublicController import public_router as static_public_router
from controllers.AcervoIndexadorController import acervo_indexador_router
from controllers.ConfiguracaoEmailController import configuracao_email_router
from controllers.PavServicesController import pav_services_router
from controllers.AssistenteIaController import assistente_ia
from controllers.AssistenteIaAdminController import assistente_ia_admin
from controllers.AssistenteIaWsController import assistente_ia_ws


def add_web_routes(app: FastAPI) -> None:
    """
    Monta os routers no app FastAPI.
    """
    auth = APIRouter(dependencies=[Depends(auth_middleware)])
    public_router = APIRouter()

   
    if env.ENV == "development":
        auth.include_router(dev_tools_router)

    # Registra os grupos no FastAPI
    app.include_router(auth)
    app.include_router(public_router)
