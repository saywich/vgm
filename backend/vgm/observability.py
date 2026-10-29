import datetime
import json
import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc import trace_exporter
from opentelemetry.instrumentation import grpc as grpc_instrumentation
from opentelemetry.sdk import resources
from opentelemetry.sdk import trace as sdk_trace
from opentelemetry.sdk.trace import export


class JsonFormatter(logging.Formatter):

    def format(self, record):
        context = trace.get_current_span().get_span_context()
        entry = {
            "timestamp":
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level":
                record.levelname,
            "service":
                os.getenv("SERVICE_NAME", "gateway"),
            "message":
                record.getMessage(),
            "trace_id":
                format(context.trace_id, "032x") if context.is_valid else ""
        }

        for key in (
            "request_id", "status", "method", "route", "duration_ms",
            "rpc_method"
        ):
            if hasattr(record, key):
                entry[key] = getattr(record, key)

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry)


def configure(service):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

    provider = sdk_trace.TracerProvider(
        resource=resources.Resource.create({"service.name": service})
    )
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        provider.add_span_processor(
            export.BatchSpanProcessor(
                trace_exporter.OTLPSpanExporter(
                    endpoint=endpoint, insecure=True
                )
            )
        )

    trace.set_tracer_provider(provider)
    grpc_instrumentation.GrpcInstrumentorClient().instrument()
    grpc_instrumentation.GrpcInstrumentorServer().instrument()
