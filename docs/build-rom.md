<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Build a ROM of your own PROGRAM files

ROM1 can load PROGRAM files other than adventures. This command builds just
the 512K data ROM. You don't need Adventure's GROM or UberGROM firmware to
run it. The [complete Adventure build](building.md) also makes the ATmega
programming files.

## Put your files in a folder

Download and extract this repository, and install Python 3.10 or later.
Inside the repository, create a folder called `local-inputs` and put your
PROGRAM files there. For example:

```text
local-inputs/
  HELLO.tfi
  MENU.tfi
  LEVEL1.tfi
  files.json
```

These example `.tfi` files must be PROGRAM files with TIFILES headers. Renaming
a file doesn't convert it to TIFILES. The [input format directions](building.md#make-your-list)
also cover raw PROGRAM bytes and files inside sector-format TI disk images.

## Make the file list

Save this as `local-inputs/files.json`, using your own filenames:

```json
{
  "files": [
    {"name": "HELLO", "path": "HELLO.tfi", "format": "tifiles"},
    {"name": "MENU", "path": "MENU.tfi", "format": "tifiles"},
    {"name": "LEVEL1", "path": "LEVEL1.tfi", "format": "tifiles"}
  ]
}
```

`name` is the TI filename after `ROM1.`; `path` locates the input relative to
this JSON file. For example, the first entry becomes `ROM1.HELLO`.

## Run the builder

Open a terminal in the repository directory and run:

```powershell
python tools/build_rom.py --files local-inputs/files.json --out output/my-rom
```

Use a new output folder each time. The builder refuses to overwrite an existing
one. For disk-image inputs, also pass `--xdt99` as described in the input directions.

You get three files in `output/my-rom/`:

| File | What it is |
| --- | --- |
| `rom1-512k.bin` | The 524,288-byte ROM image to program |
| `rom-map.txt` | Names, sizes, banks and offsets |
| `manifest.json` | File information and checksums |

The builder writes the CF01 directory, places the contents and pads the ROM.
It strips TIFILES headers and sector padding, handles files crossing banks,
and shares storage when two files have identical contents. You don't need
to calculate offsets or edit the ROM with a hex editor.

## Use it in a cartridge

The cartridge needs the ROM1 GPL loader linked into its GROM DSR list, plus
positive bank switching: a CPU write to `>6000 + 2 * bank` selects an 8K ROM
bank. The [code guide](code-guide.md#does-rom1-need-the-8k-ube1-grom-to-load-an-adventure)
explains the loader and its dependencies. This command doesn't add it to another
module or create that module's GROM image.

Your program requests PROGRAM LOAD from a name such as `ROM1.HELLO` and
supplies a VDP buffer large enough for the file. ROM1 copies the bytes there;
it doesn't automatically run them or adapt the requesting program.

The builder accepts 1-510 files, each 1-15,360 bytes, subject to the 512K total
capacity. The ROM is read-only and holds PROGRAM files; DIS/FIX and DIS/VAR
record files aren't supported by this ROM1 loader. UBE1's save service is
separate and isn't needed just to load from ROM1.
