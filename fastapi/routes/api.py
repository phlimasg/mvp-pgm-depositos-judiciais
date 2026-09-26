# app/routers/app_router.py
from fastapi import FastAPI, Depends
from fastapi.routing import APIRouter

# imports dos routers existentes
from controllers.DjoController import djo_router


def add_api_routes(app: FastAPI) -> None:
    """
    Monta os routers e adiciona middlewares no app FastAPI.
    """

    # Crie o APIRouter e aplique a dependência de autenticação
    # usando o parâmetro 'dependencies'.
    api_router = APIRouter(prefix="/api", dependencies=[Depends(basic_auth_dependency)])

    # Adicione as rotas que precisam de autenticação a este router
    
    api_router.include_router(djo_router)

    # A rota de autenticação pode ser adicionada a outro router
    # ou diretamente no 'app' para não ser protegida pelo basic auth
    # (assumindo que ela tem seu próprio mecanismo de segurança, como JWT)
    # app.include_router(auth_router)

    app.include_router(api_router)
