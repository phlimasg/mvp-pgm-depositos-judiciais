from datetime import datetime, timezone
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, with_loader_criteria
from sqlmodel import Session, create_engine

from core.BaseModel import BaseModel
from libraries.env import env


def _normalize_mssql_autos_url(url: str) -> str:
    """
    Normaliza a URL do banco autos (MSSQL).
    - mssql+pymssql://: deixada como está (não precisa de driver ODBC).
    - Com DATABASE_AUTOS_USE_PYMSSQL=True: mssql:// vira mssql+pymssql:// (usa FreeTDS).
    - Caso contrário: mssql:// vira mssql+pyodbc:// e adiciona driver ODBC se faltar.
    """
    u = url.strip().lower()
    if u.startswith("mssql+pymssql://"):
        return url
    if not u.startswith(("mssql://", "mssql+pyodbc://")):
        return url

    parsed = urlparse(url)
    if getattr(env, "DATABASE_AUTOS_USE_PYMSSQL", False):
        # pymssql não aceita parâmetros do pyodbc (encrypt, trustServerCertificate, etc.)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        drop = {"encrypt", "trustservercertificate", "schema", "requesttimeout"}
        qs = {k: v for k, v in qs.items() if k.lower() not in drop}
        new_query = urlencode(qs, doseq=True)
        return urlunparse(parsed._replace(scheme="mssql+pymssql", query=new_query))
    if parsed.scheme == "mssql":
        parsed = parsed._replace(scheme="mssql+pyodbc")
    qs = parse_qs(parsed.query, keep_blank_values=True)
    if "driver" not in qs:
        driver = env.DATABASE_AUTOS_ODBC_DRIVER or "ODBC Driver 18 for SQL Server"
        qs["driver"] = [driver]
    new_query = urlencode(qs, doseq=True)
    _driver_param = "driver="
    if _driver_param in new_query:
        start = new_query.index(_driver_param) + len(_driver_param)
        end = new_query.find("&", start)
        end = len(new_query) if end == -1 else end
        driver_val = new_query[start:end].replace("%20", "+")
        new_query = new_query[:start] + driver_val + new_query[end:]
    return urlunparse(parsed._replace(query=new_query))


# connect_timeout + statement_timeout evitam hang infinito (ex.: lock em acervo_indexador)
_PG_CONNECT_ARGS = {
    "connect_timeout": 10,
    "options": "-c statement_timeout=15000",
}

__engine = create_engine(
    env.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_PG_CONNECT_ARGS,
)
__indexador_engine = create_engine(
    env.DATABASE_URL_INDEXADOR,
    pool_pre_ping=True,
    connect_args=_PG_CONNECT_ARGS,
)
__autos_engine = create_engine(_normalize_mssql_autos_url(env.DATABASE_AUTOS_URL))
__catraca_engine = create_engine(
    env.DATABASE_URL_CATRACA,
    pool_pre_ping=True,
    connect_args=_PG_CONNECT_ARGS,
)
# SQLModel.metadata.create_all(engine)


def new_session() -> Session:
    """Sessão avulsa (persistência em background, fora do request)."""
    return Session(__engine)


def get_session():  # pragma: no cover
    with Session(__engine) as session:
        yield session


def get_indexador_session():  # pragma: no cover
    with Session(__indexador_engine) as session:
        session.info["skip_soft_delete"] = True
        yield session


def get_autos_session():  # pragma: no cover
    with Session(__autos_engine) as session:
        session.info["skip_soft_delete"] = True
        yield session


def get_catraca_session():  # pragma: no cover
    with Session(__catraca_engine) as session:
        session.info["skip_soft_delete"] = True
        yield session


# Define o deleted_at para os registros deletados
@event.listens_for(Session, "before_flush")
def __set_deleted_at(session, flush_context, instances):  # pragma: no cover
    if session.info.get("skip_soft_delete"):
        return

    for obj in session.deleted:
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(timezone.utc)
            session.add(obj)


# Filtra os registros com deleted_at nulo
@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state: ORMExecuteState):  # pragma: no cover
    if execute_state.session and execute_state.session.info.get("skip_soft_delete"):
        return

    if execute_state.is_select:

        def filtro_deleted_at(cls):
            if hasattr(cls, "deleted_at"):
                return cls.deleted_at.is_(None)
            return True

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModel,
                filtro_deleted_at,
                include_aliases=True,
            )
        )
