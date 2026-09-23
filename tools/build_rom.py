# Copyright (c) 2026 hexbus.
# SPDX-License-Identifier: Apache-2.0
"""Build a CF01 ROM of PROGRAM files without any module or AVR firmware."""
import argparse
import json
from pathlib import Path

from build import make_rom, new_output, read_adventures, sha


def build_rom(files, out, xdt99=None):
    out = new_output(out)
    # Reuse the checked input reader and exact packer from the Adventure build.
    rom, catalog = make_rom(read_adventures(files, xdt99))
    report = dict(format='CF01', device='ROM1', files=catalog,
                  outputs={'rom1-512k.bin': dict(bytes=len(rom), sha256=sha(rom))})
    text = 'ROM1 name  bytes  ROM offset  bank  bank offset\n'+''.join(
        f"{f['name']:<10} {f['bytes']:5}  >{f['rom_offset']:06X}  >{f['bank']:04X}  >{f['bank_offset']:04X}\n"
        for f in catalog)
    # All inputs and capacity checks finish before any output is created.
    out.mkdir(parents=True)
    outputs = {'rom1-512k.bin': rom,
               'manifest.json': (json.dumps(report, indent=2)+'\n').encode('utf-8'),
               'rom-map.txt': text.encode('ascii')}
    for name, data in outputs.items():
        with (out/name).open('xb') as stream:
            stream.write(data)
    print(f'Built {len(catalog)} PROGRAM files in {out / "rom1-512k.bin"}')
    print('Data ROM only. The cartridge also needs the ROM1 GPL loader and compatible bank switching.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--xdt99', type=Path)
    args = parser.parse_args()
    try:
        build_rom(**vars(args))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, str(exc)+'\n')
