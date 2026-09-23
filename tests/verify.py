# Copyright (c) 2026 hexbus.
# SPDX-License-Identifier: Apache-2.0
"""Public checks use synthetic data only; optional xdt99 rebuilds frozen code."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from build import frozen_assets, make_rom, read_adventures, tifiles_program, new_output, encode_hex, decode_hex


def rejects(action):
    try:
        action()
    except (ValueError, KeyError):
        return
    raise AssertionError('Expected rejection')


def verify(xdt99=None):
    frozen, assets = frozen_assets()
    assert assets['ube1-grom8k.bin'][8156:8167] == b'2026 Hexbus'
    assert assets['ube1-grom8k.bin'][8167:] == b'\xff'*25
    eeprom = assets['blank-eeprom.bin']
    assert eeprom[0x15] == eeprom[0x05] == 0x10
    assert eeprom[0x1d] == eeprom[0x0d] == 0xef
    assert eeprom[0x102:0x106] == b'UBF1'
    # Includes a payload spanning two ROM banks and an exact-content alias.
    large = bytes((i*13+7) % 256 for i in range(12001))
    files = {'LONG': large, 'ALIAS': large, 'SMALL': b'local synthetic test'}
    rom, catalog = make_rom(files)
    assert len(rom) == 524288 and rom[0x10:0x16] == b'CF01\0\3'
    offsets = {}
    for i in range(3):
        at = 0x20+i*16
        name = rom[at:at+10].decode().rstrip()
        size = int.from_bytes(rom[at+10:at+12], 'big')
        offset = int.from_bytes(rom[at+12:at+14], 'big')*8192+int.from_bytes(rom[at+14:at+16], 'big')
        assert rom[offset:offset+size] == files[name]
        offsets[name] = offset
    assert offsets['LONG'] == offsets['ALIAS']
    rejects(lambda: make_rom({}))
    rejects(lambda: make_rom({f'N{i}': bytes([i])*15360 for i in range(35)}))
    rejects(lambda: new_output(ROOT/'release'))
    rejects(lambda: new_output(ROOT/'output'))
    (ROOT/'output').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='public-check-', dir=ROOT/'output') as temp:
        temp = Path(temp)
        rejects(lambda: new_output(temp))
        payload = bytes(range(256))+b'boundary'
        header = bytearray(128);header[:8] = b'\x07TIFILES'
        header[8:10] = b'\0\2';header[10] = 1;header[12] = 8
        tif = bytes(header)+payload.ljust(512, b'\0')
        assert tifiles_program(tif) == payload
        rejects(lambda: tifiles_program(tif[:-1]))
        invalid = bytearray(tif);invalid[10] = 0x80
        rejects(lambda: tifiles_program(invalid))
        (temp/'test.tfi').write_bytes(tif)
        manifest = temp/'files.json'
        entry = dict(name='TEST', path='test.tfi', format='tifiles')
        manifest.write_text(json.dumps(dict(files=[entry])))
        assert read_adventures(manifest) == {'TEST': payload}
        manifest.write_text(json.dumps(dict(files=[entry, entry])))
        rejects(lambda: read_adventures(manifest))
        entry['format'] = 'raw'
        manifest.write_text(json.dumps(dict(files=[entry])))
        rejects(lambda: read_adventures(manifest))
        # Exercise HEX records crossing 64K, using an independent address check.
        data = bytes(i % 251 for i in range(0x20000))
        decoded = decode_hex(encode_hex(data))
        assert bytes(decoded[i] for i in range(len(data))) == data
        if xdt99:
            xdt99 = Path(xdt99).resolve()
            for name, source, expected in [
                ('ube1', ROOT/'sources/gpl/ubf1-compact/ube1.gpl', assets['ube1-grom8k.bin'][:8167]),
                ('rom1', ROOT/'sources/gpl/rom1/rom1.gpl', assets['rom1-loader.bin'])]:
                binary = temp/(name+'.bin')
                subprocess.run([sys.executable, str(xdt99/'xga99.py'), str(source), '-o', str(binary)], check=True)
                assert binary.read_bytes() == expected, name+' is not byte-identical'
            sys.path.insert(0, str(xdt99))
            from xdm99 import File
            assert File.create_from_tif_image(tif, hostfn=str(temp/'test.tfi')).get_contents() == payload
    print(json.dumps(dict(passed=True, frozen_assets=True, synthetic_packing=True,
                         input_rejections=True, source_rebuilt=bool(xdt99))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xdt99', type=Path)
    verify(parser.parse_args().xdt99)
