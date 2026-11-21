#!/usr/bin/env python3
"""Point the storage root layout at the GPT partition named by UNIXNU_STORAGE_PARTITION.

The kernel reads its root manifest from the first block of the GPT partition that the ShengUfs root
layout names, and upstream that name is "userdata". A device that keeps Android's userdata and gives
UniXNU a partition of its own (for example "apple") builds with UNIXNU_STORAGE_PARTITION=apple; this
step writes that name into the driver source before the ShengUfs and source-storage archives build.
The name keeps its default ("userdata") when the variable is empty.

Run from the build tree, before component:ShengUfs (the board lists it there).
"""
import os
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r'[A-Za-z0-9._-]{1,32}')
WANTED_PATTERN = re.compile(r'static const char wanted\[\] = "[^"]*";')


def main() -> int:
    name = os.environ.get('UNIXNU_STORAGE_PARTITION', '').strip() or 'userdata'
    if not NAME_PATTERN.fullmatch(name):
        return fail(f'UNIXNU_STORAGE_PARTITION must be 1-32 characters of [A-Za-z0-9._-], not {name!r}')
    path = Path('drivers/ShengUfs/RootLayout.h')
    if not path.is_file():
        return fail(f'{path} not found; run this step from the build tree')
    text = path.read_text()
    updated, count = WANTED_PATTERN.subn(f'static const char wanted[] = "{name}";', text)
    if count != 1:
        return fail(f'{path}: expected one wanted[] declaration, found {count}')
    if updated != text:
        path.write_text(updated)
    print(f'storage root partition: {name}')
    return 0


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
