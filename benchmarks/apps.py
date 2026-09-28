"""Equivalent HTTP workloads; return freshly constructed responses on each request."""
from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.responses import Response as FastAPIResponse

from karak import Karak
from karak import Request
from karak import ResourceContext
from karak import Response
from karak import Router


def karak_response(body: bytes) -> Response:
    return Response(content=body, headers={
        "content-type": "text/plain; charset=utf-8",
        "content-length": str(len(body)),
    })


def fastapi_response(body: bytes) -> FastAPIResponse:
    return FastAPIResponse(content=body, media_type="text/plain")


router = Router()
fastapi_app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)


@router.get("/text")
async def karak_text():
    return karak_response(b"Hello, world!")


@fastapi_app.get("/text")
async def fastapi_text():
    return fastapi_response(b"Hello, world!")


@router.get("/users/{user_id}")
async def karak_typed(user_id: int, active: bool = True, limit: int = 10):
    return karak_response(f"{user_id}:{active}:{limit}".encode())


@fastapi_app.get("/users/{user_id}")
async def fastapi_typed(user_id: int, active: bool = True, limit: int = 10):
    return fastapi_response(f"{user_id}:{active}:{limit}".encode())


@router.get("/context")
async def karak_context(context: ResourceContext[Request]):
    request = context.value
    body = f"{request.headers.get('x-client')}:{request.cookies.get('theme')}"
    return karak_response(body.encode())


@fastapi_app.get("/context")
async def fastapi_context(request: FastAPIRequest):
    body = f"{request.headers.get('x-client')}:{request.cookies.get('theme')}"
    return fastapi_response(body.encode())


@router.post("/body")
async def karak_body(context: ResourceContext[Request]):
    return karak_response(await context.value.body())


@fastapi_app.post("/body")
async def fastapi_body(request: FastAPIRequest):
    return fastapi_response(await request.body())


karak_app = Karak(router=router)
