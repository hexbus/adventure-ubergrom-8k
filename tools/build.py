# Copyright (c) 2026 hexbus.
# SPDX-License-Identifier: Apache-2.0
"""Pack user-supplied Adventure inputs around the frozen ROM1/UBE1 code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def frozen_assets():
    manifest = json.loads((ROOT/'release/frozen.json').read_text())
    assets = {}
    for name, expected in manifest['files'].items():
        data = (ROOT/'release'/name).read_bytes()
        if len(data) != expected['bytes'] or sha(data) != expected['sha256']:
            raise ValueError('Frozen asset changed: '+name)
        assets[name] = data
    return manifest, assets


def new_output(value):
    """Only new folders under output/; never overwrite inputs or releases."""
    target = Path(value).resolve()
    parent = ROOT/'output'
    if target == parent or not target.is_relative_to(parent) or target.exists():
        raise ValueError('Choose a NEW directory below this repository\'s output/')
    return target


def tifiles_program(data):
    # TIFILES has a 128-byte header and sector-padded PROGRAM contents.
    if len(data) < 128 or data[:8] != b'\x07TIFILES':
        raise ValueError('Expected a TIFILES header; use format raw for raw PROGRAM data')
    if data[10] & 0x83 != 1:
        raise ValueError('Adventure ROM1 supports PROGRAM files only')
    sectors = int.from_bytes(data[8:10], 'big')
    if not sectors or len(data) != 128+sectors*256:
        raise ValueError('TIFILES sector count does not match its size')
    size = (sectors-1)*256+(data[12] or 256)
    return data[128:128+size]


def read_adventures(manifest_path, xdt99=None):
    manifest_path = Path(manifest_path).resolve()
    records = json.loads(manifest_path.read_text())['files']
    if not isinstance(records, list) or not 1 <= len(records) <= 510:
        raise ValueError('Supply between 1 and 510 named PROGRAM files')
    files = {}
    disks = {}
    for record in records:
        name = record['name']
        # Slash is used in some original TI names; dot is the device separator.
        if not isinstance(name, str) or not re.fullmatch(r"[A-Z0-9_/'-]{1,10}", name):
            raise ValueError('Names need 1-10 uppercase letters, digits, underscore, slash, apostrophe or hyphen')
        if name in files:
            raise ValueError('Duplicate ROM1 filename: '+name)
        source = (manifest_path.parent/record['path']).resolve()
        kind = record['format']
        if kind == 'disk':
            if xdt99 is None:
                raise ValueError('Disk input needs --xdt99 pointing to an xdt99 checkout')
            sys.path.insert(0, str(Path(xdt99).resolve()))
            from xdm99 import Disk, Xdm99Console
            if source not in disks:
                raw = source.read_bytes()
                if len(raw) % 256 or raw[13:16] != b'DSK':
                    raise ValueError('Expected a sector-based TI DSK, not a PC99 track image')
                disks[source] = Disk(raw, Xdm99Console())
            entry = disks[source].catalog[record['file']]
            if entry.fd.flags & 0x83 != 1:
                raise ValueError('Selected disk file is not PROGRAM: '+name)
            payload = entry.get_contents()
        elif kind == 'tifiles':
            payload = tifiles_program(source.read_bytes())
        elif kind == 'raw':
            payload = source.read_bytes()
            if payload.startswith(b'\x07TIFILES'):
                raise ValueError('TIFILES header detected; set format to tifiles')
        else:
            raise ValueError('Unknown format: '+str(kind))
        if not 1 <= len(payload) <= 0x3c00:
            raise ValueError('Adventure PROGRAM payload must be 1..15360 bytes: '+name)
        files[name] = payload
    return files


def make_rom(files):
    """CF01: bank zero directory, 16-byte entries, deduplicated PROGRAM data."""
    if not 1 <= len(files) <= 510:
        raise ValueError('ROM1 needs 1..510 files')
    rom = bytearray(8192)
    rom[0x10:0x14] = b'CF01'
    rom[0x14:0x16] = struct.pack('>H', len(files))
    packed, catalog = {}, []
    for i, (name, payload) in enumerate(sorted(files.items())):
        # Compare actual bytes, not just hashes, when sharing an exact duplicate.
        offset = packed.get(payload)
        if offset is None:
            rom.extend(b'\0'*(len(rom) % 2))
            offset = len(rom)
            if offset+len(payload) > 0x80000:
                raise ValueError('Adventure files exceed the 512 KiB ROM')
            rom.extend(payload)
            packed[payload] = offset
        bank, within = divmod(offset, 8192)
        rom[0x20+i*16:0x30+i*16] = name.encode('ascii').ljust(10, b' ')+struct.pack('>HHH', len(payload), bank, within)
        catalog.append(dict(name=name, bytes=len(payload), rom_offset=offset,
                            bank=bank, bank_offset=within, sha256=sha(payload)))
    # Preserve the original packer's power-of-two zero padding, then the
    # hardware packager's erased-byte padding out to the physical 512K chip.
    image_size = 1 << (len(rom)-1).bit_length()
    rom.extend(b'\0'*(image_size-len(rom)))
    rom.extend(b'\xff'*(0x80000-len(rom)))
    return bytes(rom), catalog


def decode_hex(data):
    memory, base, eof = {}, 0, False
    for line in data.decode('ascii').splitlines():
        if not line.startswith(':') or eof:
            raise ValueError('Invalid Intel HEX record order')
        record = bytes.fromhex(line[1:])
        count, address, kind = record[0], int.from_bytes(record[1:3], 'big'), record[3]
        if len(record) != count+5 or sum(record) % 256:
            raise ValueError('Invalid Intel HEX checksum or length')
        payload = record[4:-1]
        if kind == 0:
            for i, value in enumerate(payload):
                at = base+address+i
                if at in memory or at >= 0x20000:
                    raise ValueError('Overlapping/out-of-range Flash record')
                memory[at] = value
        elif kind in (2, 4) and count == 2:
            base = int.from_bytes(payload, 'big') << (4 if kind == 2 else 16)
        elif kind == 1 and count == 0:
            eof = True
        elif kind not in (3, 5):
            raise ValueError('Unsupported Intel HEX record')
    if not eof:
        raise ValueError('Missing Intel HEX EOF')
    return memory


def encode_hex(data):
    def line(at, kind, payload):
        raw = bytes([len(payload)])+at.to_bytes(2, 'big')+bytes([kind])+payload
        return ':'+(raw+bytes([-sum(raw) & 255])).hex().upper()
    lines = []
    for offset in range(0, len(data), 16):
        if offset % 65536 == 0:
            lines.append(line(0, 4, (offset >> 16).to_bytes(2, 'big')))
        lines.append(line(offset & 65535, 0, data[offset:offset+16]))
    return ('\n'.join(lines+[line(0, 1, b'')])+'\n').encode('ascii')


def images(original, firmware, assets, frozen, rom):
    if len(original) != 6144 or sha(original) != frozen['original_adventure_sha256']:
        raise ValueError('Supply the original supported 6144-byte phm3041g3.bin Adventure GROM')
    if sha(firmware) != frozen['firmware_hex_sha256']:
        raise ValueError('Supply the supported unmodified UberGROM dist/GROMSim/ubergrom.hex')
    decoded = decode_hex(firmware)
    boot = bytes(decoded.get(at, 255) for at in range(0x1e000, 0x20000))
    if sha(boot) != frozen['firmware_boot_sha256']:
        raise ValueError('Unexpected UberGROM firmware region')
    grom = bytearray(b'\xff'*0x8000)
    grom[:8192] = original.ljust(8192, b'\0')
    grom[8:10] = b'\x78\x00'  # Link ROM1 into Adventure's unused DSR list.
    loader = assets['rom1-loader.bin']
    grom[0x1800:0x1800+len(loader)] = loader
    grom[0x2000:0x4000] = assets['ube1-grom8k.bin']
    flash = bytearray(b'\xff'*0x20000)
    flash[:0x8000], flash[0x1e000:] = grom, boot
    eeprom = assets['blank-eeprom.bin']
    return {'adventure-rom512k.bin': rom, 'adventureG.bin': bytes(grom),
            'adventure-ubergrom-flash-atmega1284p.bin': bytes(flash),
            'adventure-ubergrom-eeprom-atmega1284p.bin': eeprom,
            'adventure-ubergrom-whole-atmega1284p.bin': bytes(flash)+eeprom,
            'adventure-ubergrom-flash-atmega1284p.hex': encode_hex(flash),
            'adventure-ubergrom-eeprom-atmega1284p.hex': encode_hex(eeprom)}


def build(adventures, grom, firmware, out, xdt99=None):
    out = new_output(out)
    frozen, assets = frozen_assets()
    files = read_adventures(adventures, xdt99)
    rom, catalog = make_rom(files)
    result = images(Path(grom).read_bytes(), Path(firmware).read_bytes(), assets, frozen, rom)
    for name in ('NOTICE.txt', 'LICENSE-CODE.txt'):
        result[name] = (ROOT/name).read_bytes()
    # Validate everything before making the output directory.
    out.mkdir(parents=True)
    for name, data in result.items():
        with (out/name).open('xb') as stream:
            stream.write(data)
    report = dict(release=frozen['release'], format='CF01', files=catalog,
                  fuses=frozen['fuses'], blank_eeprom=True, firmware_modified=False,
                  outputs={name:dict(bytes=len(data), sha256=sha(data)) for name, data in result.items()})
    (out/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    (out/'rom-map.txt').write_text('ROM1 name  bytes  ROM offset  bank  bank offset\n'+''.join(
        f"{f['name']:<10} {f['bytes']:5}  >{f['rom_offset']:06X}  >{f['bank']:04X}  >{f['bank_offset']:04X}\n" for f in catalog))
    print('Built '+str(len(catalog))+' adventures in '+str(out))
    print('EEPROM is blank. Preserve existing saves before programming. See docs/programming.md.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adventures', required=True, type=Path)
    parser.add_argument('--grom', required=True, type=Path)
    parser.add_argument('--firmware', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--xdt99', type=Path)
    args = parser.parse_args()
    try:
        build(**vars(args))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, str(exc)+'\n')
