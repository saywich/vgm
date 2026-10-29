import datetime
import functools
import json
import logging
import os
import uuid

import grpc
import psycopg
from psycopg import rows
import psycopg_pool
import pydantic

from vgm.generated import vgm_pb2
from vgm.generated import vgm_pb2_grpc

HTTP_TO_GRPC = {
    400: grpc.StatusCode.INVALID_ARGUMENT,
    401: grpc.StatusCode.UNAUTHENTICATED,
    403: grpc.StatusCode.PERMISSION_DENIED,
    404: grpc.StatusCode.NOT_FOUND,
    409: grpc.StatusCode.ALREADY_EXISTS,
    422: grpc.StatusCode.FAILED_PRECONDITION,
    429: grpc.StatusCode.RESOURCE_EXHAUSTED,
    503: grpc.StatusCode.UNAVAILABLE,
    504: grpc.StatusCode.DEADLINE_EXCEEDED
}
GRPC_TO_HTTP = {v: k for k, v in HTTP_TO_GRPC.items()}


class AppError(Exception):

    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


def encode(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()

    if isinstance(value, uuid.UUID):
        return str(value)

    raise TypeError(f"Cannot serialize {type(value)}")


def payload(value):
    return vgm_pb2.Payload(json=json.dumps(value, default=encode))


def rpc(contract):

    def decorate(fn):

        @functools.wraps(fn)
        def wrapped(self, request, context):
            try:
                data = contract.model_validate_json(request.json)
                return payload(fn(self, data))
            except pydantic.ValidationError as exc:
                details = "; ".join(
                    f"{'.'.join(map(str, e['loc']))}: {e['msg']}"
                    for e in exc.errors()
                )
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, details)
            except AppError as exc:
                context.abort(
                    HTTP_TO_GRPC.get(exc.status, grpc.StatusCode.INTERNAL),
                    exc.message
                )
            except grpc.RpcError as exc:
                context.abort(exc.code(), exc.details())
            except (psycopg.OperationalError, psycopg_pool.PoolTimeout):
                logging.exception("database_unavailable")
                context.abort(
                    grpc.StatusCode.UNAVAILABLE,
                    "The database is temporarily unavailable"
                )
            except Exception:
                logging.exception(
                    "rpc_failed", extra={"rpc_method": fn.__name__}
                )
                context.abort(
                    grpc.StatusCode.INTERNAL,
                    "An internal service error occurred"
                )

        return wrapped

    return decorate


def database():
    return psycopg_pool.ConnectionPool(
        os.environ["DATABASE_URL"],
        min_size=1,
        max_size=10,
        timeout=5,
        kwargs={"row_factory": rows.dict_row},
        open=True
    )


def client(service):
    address = os.getenv(f"{service.upper()}_ADDRESS", f"{service}:50051")
    channel = grpc.insecure_channel(
        address, options=[("grpc.max_receive_message_length", 2 * 1024 * 1024)]
    )
    return getattr(vgm_pb2_grpc, f"{service.capitalize()}Stub")(channel)


def call(stub, method, data):
    return json.loads(getattr(stub, method)(payload(data), timeout=12).json)
