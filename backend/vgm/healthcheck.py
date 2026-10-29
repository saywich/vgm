import os

import grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc


def main():
    address = os.getenv("HEALTH_ADDRESS", "localhost:50051")
    with grpc.insecure_channel(address) as channel:
        stub = health_pb2_grpc.HealthStub(channel)
        response = stub.Check(health_pb2.HealthCheckRequest(), timeout=3)

    if response.status != health_pb2.HealthCheckResponse.SERVING:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
