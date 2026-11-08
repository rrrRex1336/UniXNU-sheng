#!/usr/bin/env bash
# Device packaging script, identical in every device repository. Do not edit it: a board changes board.toml
# ([package] and the sections it names), never this file. Steps (run by "unixnu release"): deps, preflight,
# patches, build, pack, verify. Documentation: docs/porting/packaging.md in the UniXNU repository.
# usage: scripts/package.sh [--os 17|26|27|PROFILE] [--no-deps] [--check] [any other unixnu option]
set -euo pipefail
DEVICE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
UNIXNU=$(python3 - "$DEVICE/board.toml" <<'PY'
import sys, tomllib
package = tomllib.load(open(sys.argv[1], 'rb')).get('package', {})
if 'unixnu' not in package:
    sys.exit('board.toml needs [package] unixnu = "<path of the UniXNU checkout, relative to this repository>"')
print(package['unixnu'])
PY
)
case "$UNIXNU" in /*) ROOT=$UNIXNU ;; *) ROOT=$(cd "$DEVICE/$UNIXNU" && pwd) ;; esac
# The pinned upstream Turnip frame diagnostics patch creates tu_frame_diagnostic.h
# but omits Git's required new-file mode header. Without it, git apply treats
# /dev/null as a source path and fails with "dev/null: No such file or directory".
# Repair the checked-out upstream patch before unixnu applies and validates it.
python3 - "$ROOT/patches/mesa/turnip-frame-diagnostics.patch" <<'PY'
from pathlib import Path
import sys

patch = Path(sys.argv[1])
text = patch.read_text()
header = (
    'diff --git a/src/freedreno/vulkan/tu_frame_diagnostic.h '
    'b/src/freedreno/vulkan/tu_frame_diagnostic.h\n'
)
if header not in text:
    raise SystemExit(f'Expected new-file section not found in {patch}')
if header + 'new file mode 100644\n' not in text:
    text = text.replace(header, header + 'new file mode 100644\n', 1)
    patch.write_text(text)
PY
exec python3 "$ROOT/unixnu" release -D "$DEVICE" "$@"
