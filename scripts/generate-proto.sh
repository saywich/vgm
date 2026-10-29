#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python -m grpc_tools.protoc -I proto --python_out=backend/vgm/generated --grpc_python_out=backend/vgm/generated proto/vgm.proto
python - <<'PY'
from pathlib import Path
p = Path('backend/vgm/generated/vgm_pb2_grpc.py')
p.write_text(p.read_text().replace('import vgm_pb2 as', 'from . import vgm_pb2 as'))
PY

python scripts/clean_generated.py
