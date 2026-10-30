from concurrent import futures
import logging
import os
import signal

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from vgm import common
from vgm import identity
from vgm import messaging
from vgm import observability
from vgm import video
from vgm.generated import vgm_pb2_grpc


def main():
    name = os.environ["SERVICE_NAME"]
    observability.configure(name)

    pool = common.database() if name != "video" else None
    if pool:
        pool.wait(timeout=20)

    service: type[identity.Identity] | type[messaging.Messaging
                                           ] | type[video.Video] = {
                                               "identity": identity.Identity,
                                               "messaging": messaging.Messaging,
                                               "video": video.Video
                                           }[name]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[("grpc.max_receive_message_length", 65536)]
    )
    getattr(vgm_pb2_grpc, f"add_{name.capitalize()}Servicer_to_server"
           )(service(pool) if pool else service(), server)

    check = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(check, server)
    check.set("", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(os.getenv("GRPC_BIND", "[::]:50051"))
    server.start()
    logging.info("service_ready")

    def shutdown(*_):
        check.enter_graceful_shutdown()
        server.stop(5).wait()
        if pool:
            pool.close()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
