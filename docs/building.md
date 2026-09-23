<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Build your own Adventure cartridge

Use Python 3.10 or later. Normal builds use the frozen binary components and
do not need an assembler. The optional disk-image reader and source-rebuild
check use [xdt99](https://github.com/endlos99/xdt99).

## Get the inputs

Keep downloaded files under `local-inputs/`, which Git and the release exporter
exclude. Inputs are never uploaded or fetched automatically by the builder.

| Input | Source and file to use |
| --- | --- |
| Original Adventure module | [WHTech MAME cartridges](https://ftp.whtech.com/#Cartridges%2FMAME%2Fzip): extract `phm3041g3.bin` from `advent.zip` |
| Adventure game disks | [WHTech Adventure disks](https://ftp.whtech.com/#Diskettes%2FCartridge_Disks%2FAdventure): choose your games; the builder reads ordinary sector-based TI DSK images |
| UberGROM firmware | [Tursi's UberGROM](https://github.com/tursilion/ubergrom): use `dist/GROMSim/ubergrom.hex`, unchanged |

The cartridge directory also offers an `all_carts.zip` collection under
`Cartridges/MAME/`. The individual
[advent.zip download](https://ftp.whtech.com/?do=download&file=Cartridges%2FMAME%2Fzip%2Fadvent.zip)
is sufficient. The documented
[PIRATE disk download](https://ftp.whtech.com/?do=download&file=Diskettes%2FCartridge_Disks%2FAdventure%2FPirates_Adventure_PHD5043.dsk)
contains a PROGRAM file named `PIRATE`. These paths and that build example were
checked on September 23, 2026.
WHTech is an archive of original material; original credits and rights remain.
The exact supported module and firmware SHA-256 values are in
[release/frozen.json](../release/frozen.json). The builder refuses an unexpected
module or firmware rather than silently changing this frozen runtime.

## Choose the files

Create a JSON file listing the names you want under ROM1. Paths are relative
to that JSON file. For example, `local-inputs/adventures.json` can contain:

```json
{
  "files": [
    {"name": "MYGAME", "path": "MYGAME.tfi", "format": "tifiles"}
  ]
}
```

Supported formats:

- `tifiles`: a PROGRAM file with its 128-byte TIFILES header. The builder removes
  the header and sector padding according to its length fields.
- `raw`: only the original PROGRAM payload, without a TIFILES header or disk
  metadata. A `.bin` extension alone does not identify the contents.
- `disk`: select one PROGRAM file from a sector-based TI disk. Add a `file`
  field containing its on-disk filename and pass `--xdt99` when building.

Example disk entry:

```json
{"name": "PIRATE", "path": "Pirates_Adventure_PHD5043.dsk", "format": "disk", "file": "PIRATE"}
```

Check each disk's catalog for the actual filename. PC99 track-format disks
must first be converted or their PROGRAM files exported to TIFILES.

ROM1 names are 1-10 uppercase letters, digits, underscores, hyphens, apostrophes
or slashes.
You choose which version to include: `MISSION` is not forced to a particular
edition. Duplicate names are rejected; different names with identical payloads
share storage. A payload may occupy at most 15,360 bytes, and the whole ROM must
fit in 512 KiB. This checks packaging, not the gameplay correctness of your data.

## Build

Run from this repository, using a new output folder each time:

```powershell
python tools/build.py --adventures local-inputs/adventures.json --grom local-inputs/phm3041g3.bin --firmware local-inputs/ubergrom.hex --out output/my-cartridge
```

For disk entries, append `--xdt99 E:/git/xdt99` (or your xdt99 checkout).
The build writes the programming images, `manifest.json` with file hashes,
and `rom-map.txt` with each filename, length, bank and byte offset.
It never writes to a programmer or changes an existing output folder.
Follow the [programming directions](programming.md).
