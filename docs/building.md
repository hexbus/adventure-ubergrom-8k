<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Put your own adventures in the cartridge

You'll need Python 3.10 or later. The normal build uses the finished GROM and
loader, so you don't have to assemble anything. If you want to read files
straight from a disk image, or rebuild the GPL source, you'll also need
[xdt99](https://github.com/endlos99/xdt99).

## Get the files

Put your downloads in `local-inputs/`. That directory stays out of Git and the
GitHub release copy. The builder uses the files you give it; it doesn't download
or upload them.

| What you need | Where to get it |
| --- | --- |
| Original Adventure GROM | [WHTech MAME cartridges](https://ftp.whtech.com/#Cartridges%2FMAME%2Fzip): get `advent.zip` and extract `phm3041g3.bin` |
| Adventure disks | [WHTech Adventure disks](https://ftp.whtech.com/#Diskettes%2FCartridge_Disks%2FAdventure): pick the adventures you want |
| UberGROM firmware | [Tursi's UberGROM](https://github.com/tursilion/ubergrom): use the unchanged `dist/GROMSim/ubergrom.hex` |

You only need the individual
[advent.zip](https://ftp.whtech.com/?do=download&file=Cartridges%2FMAME%2Fzip%2Fadvent.zip),
although WHTech also has `all_carts.zip` under `Cartridges/MAME/`.
The [Pirate Adventure disk](https://ftp.whtech.com/?do=download&file=Diskettes%2FCartridge_Disks%2FAdventure%2FPirates_Adventure_PHD5043.dsk)
has a PROGRAM file named `PIRATE`. I checked these paths and built that example
on September 23, 2026. The material on WHTech still belongs to its original authors.

The builder checks the original GROM and firmware against the hashes in
[release/frozen.json](../release/frozen.json). If they don't match, it stops.
That keeps an unexpected module or firmware revision out of this frozen build.

## Make your list

Make a JSON file with the names you want to use after `ROM1.`. File paths are
relative to that JSON file. For example, put this in
`local-inputs/adventures.json`:

```json
{
  "files": [
    {"name": "MYGAME", "path": "MYGAME.tfi", "format": "tifiles"}
  ]
}
```

There are three ways to supply a game:

- **`tifiles`** is a PROGRAM file with a 128-byte TIFILES header. The builder
  takes off the header and uses its length fields to remove sector padding.
- **`raw`** is just the PROGRAM data, with no file header or disk information.
  A file ending in `.bin` isn't necessarily raw - check what it contains.
- **`disk`** takes a PROGRAM file from a normal sector-based TI disk image.
  Add `file` for the name on the disk, and pass `--xdt99` when you build.

For the WHTech Pirate disk, the entry inside your `files` list would be:

```json
{"name": "PIRATE", "path": "Pirates_Adventure_PHD5043.dsk", "format": "disk", "file": "PIRATE"}
```

Check the catalog for other disks' filenames. PC99 track-format disks need to
be converted first, or you can export their PROGRAM files to TIFILES.

Names can be 1-10 uppercase letters, digits, underscores, hyphens, apostrophes
or slashes. You can use your own version of `MISSION`, for example. I don't
force a particular edition. You can't use the same name twice, but two names
with exactly the same data share one copy in the ROM.

Each game file can be up to 15,360 bytes, and everything has to fit in the
512K ROM. The builder checks that it fits; it can't tell you whether somebody
modified or damaged the game itself.

## Build it

From the repository directory, run:

```powershell
python tools/build.py --adventures local-inputs/adventures.json --grom local-inputs/phm3041g3.bin --firmware local-inputs/ubergrom.hex --out output/my-cartridge
```

If your list uses disk images, add `--xdt99 E:/git/xdt99`, using the path to
your own xdt99 directory.

Use a new output directory for each build. The builder won't overwrite an old
one. You'll get the programming files, a `manifest.json` with their hashes,
and a `rom-map.txt` showing the filenames, sizes, banks and offsets.

It doesn't program the chips. That's the next step in the
[programming directions](programming.md).
