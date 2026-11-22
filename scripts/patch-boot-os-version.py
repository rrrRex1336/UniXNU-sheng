#!/usr/bin/env python3
"""Set the Android boot header's os_version word of a built boot image.

The sheng bootloader enforces anti-rollback: it refuses an image whose os_version is below the
device's current index. A build that must boot next to Android has to carry Android's own word,
which this step writes after packaging.

usage: patch-boot-os-version.py boot.img 0x220001a8
"""
import argparse
import struct
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('os_version', type=lambda v: int(v, 0))
    a = ap.parse_args()
    with open(a.image, 'rb') as f:
        data = bytearray(f.read())
    if data[:8] != b'ANDROID!':
        return fail('not an Android boot image')
    header_version, = struct.unpack_from('<I', data, 0x28)
    if header_version != 0:
        return fail(f'expected a version 0 boot header, got {header_version}')
    struct.pack_into('<I', data, 0x2c, a.os_version)
    with open(a.image, 'wb') as f:
        f.write(data)
    print(f'{a.image}: os_version {a.os_version:#x}')
    return 0


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
