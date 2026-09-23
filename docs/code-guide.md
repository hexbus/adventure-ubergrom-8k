<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# What's going on in the code?

There are two jobs here. **ROM1** loads an adventure from the bank-switched
ROM. **UBE1** saves files in UberGROM's EEPROM. Adventure calls them through
the console's file routines.

The source is TI **Graphics Programming Language (GPL)**. Here's where to look:

| Source | What it handles |
| --- | --- |
| [rom1.gpl](../sources/gpl/rom1/rom1.gpl) | Finds a PROGRAM file in ROM and copies it into the caller's VDP buffer |
| [ube1.gpl](../sources/gpl/ubf1-compact/ube1.gpl) | GROM header, file requests, directory checks, block allocation, PROGRAM files and EEPROM writes |
| [records.gpl](../sources/gpl/ubf1-compact/records.gpl) | The one open record file, its buffer and the current record position |
| [directory.gpl](../sources/gpl/ubf1-compact/directory.gpl) | File listings and the free-block count |
| [manager.gpl](../sources/gpl/ubf1-compact/manager.gpl) | SAVED GAMES, including marking, copying and deleting |
| [basic-cat.gpl](../sources/gpl/ubf1-compact/basic-cat.gpl) | BASIC CALL CAT and the catalog/display routines it shares with the menu |
| [scratch.gpl](../sources/gpl/ubf1-compact/scratch.gpl) | Small routines used in several places to save code space |

## Does ROM1 need the 8K UBE1 GROM to load an adventure?

**No. The 318-byte ROM1 loader does the whole PROGRAM LOAD itself.** It finds
the name in the ROM directory, switches banks and copies the contents into
the caller's VDP buffer. It doesn't call UBE1 or use its EEPROM or working RAM.

It does need the console's GPL/file routines, a cartridge header that points
to its DSR entry, and a CF01 ROM using the bank switching shown in `rom1.gpl`.
The 512K ROM contains the directory and adventure data; the loader is GPL code
in Adventure's GROM tail.

The separate 8K UBE1 GROM adds the other features:

| What you want to do | Which part handles it |
| --- | --- |
| Load `ROM1.PIRATE` | The 318-byte ROM1 loader |
| Save or reload `UBE1.PIRATE` | The UBE1 file service in the 8K GROM |
| Use BASIC DELETE on a UBE1 file | The UBE1 file service |
| Use the SAVED GAMES menu | The menu and UBE1 file service in the 8K GROM |
| Use `CALL CAT("UBE1")` | The BASIC catalog and UBE1 file service in the 8K GROM |
| Use `CALL CAT("ROM1")` | The BASIC catalog in the 8K GROM, reading the ROM directory directly |

That last one is easy to miss: **loading from ROM1 and displaying its catalog
are separate jobs**. The small ROM1 loader has no catalog, OPEN, READ or record
file support. It handles PROGRAM LOAD, rejects SAVE as write-protected, and
rejects the other operations. It's enough to load our adventures, but it isn't
a full disk DSR.

Within the 8K GROM, the menu and BASIC catalog share `CATREADDIR` and `CATTABLE`.
The first asks UBE1 for file information; the second draws the rows. The ROM1
catalog has its own directory reader because CF01 is a different format. These
source files are assembled together; they aren't separately loadable services.

## When a program asks for a file

The console finds our device name in the GROM header. It passes a **PAB** -
the block describing the file operation - in VDP memory.

UBE1 remembers the caller's GROM base, switches to base 14, checks the mapping
and reads the directory. It does the requested operation or returns a TI error.
Before returning, it locks EEPROM again and puts the caller's GROM base back.
It doesn't decide to format the EEPROM if something looks wrong.

PROGRAM LOAD and SAVE deal with the whole file. For record files, OPEN puts
the file in a 3,616-byte working buffer, READ and WRITE use that buffer, and
CLOSE saves the changes.

The file manager uses these same file operations. It doesn't have its own way
of editing EEPROM. BASIC CALL CAT shares the catalog code too, and saves and
restores BASIC's screen and scratch space so BASIC can carry on afterward.

## Where did we put it all?

The little **318-byte ROM1 loader goes in Adventure's unused 2K GROM tail**,
starting at `>7800`. The original 6K Adventure occupies `>6000->77FF`; we point
its unused DSR-list entry at our loader. UBE1 gets the next 8K slot.

| Base / address | What's there |
| --- | --- |
| Base 0, `>6000->7FFF` | Adventure plus the ROM1 loader |
| Base 1, `>6000->7FFF` | That same Flash page, so REVIEW MODULE LIBRARY stays off the menu |
| Base 0, `>8000->9FFF` | UBE1, the file manager, CALL CAT and our signature |
| Base 14, `>6000` | Working RAM; we reserve 5,632 bytes |
| Base 14, `>8000` | The same UBE1 code page |
| Bases 0 and 14, `>A000->AFFF` | EEPROM |
| Base 15 | The firmware's configuration and unlock interface |

Think of the bases as shelves with the same numbered spaces. The address picks
a space; the base picks which shelf you're looking at. Bases 0 and 1 point to
the same Adventure GROM, while base 14 lets us reach RAM at that same address.
Those bases are separate from the 8K banks in the U2 adventure ROM.

These are the mappings for this Adventure cartridge. Pairing UBE1 with another
module means checking what that module already uses.

## What do the two file systems look like?

Think of **ROM1 as the shelf of adventures** and **UBE1 as the place for your
saved games**. Each has a directory: a list of names and enough information to
find each file's contents.

| Device | What's stored there | Can we change it from the TI? |
| --- | --- | --- |
| ROM1 | The adventures included when we build the cartridge | No; rebuild and reprogram the ROM to change them |
| UBE1 | Saved games and other files | Yes; save, copy and delete files |

UBE1 keeps its files in **EEPROM**, so they survive turning the TI off. The
UberGROM RAM mentioned above is temporary working space, not the save disk.

### ROM1: a list of adventures, followed by their data

Here's a simplified picture of the 512K ROM:

```text
Bank 0: directory
  PIRATE  -> where PIRATE starts, and how many bytes to load
  VOODOO  -> where VOODOO starts, and how many bytes to load

Banks 1 onward: file contents
  [ PIRATE adventure data ][ VOODOO adventure data ][ ... ]
```

When Adventure asks for `ROM1.PIRATE`, the loader finds `PIRATE` in that list,
switches to the right ROM bank and copies the file into VDP memory. A file can
continue across a bank boundary; it doesn't need a whole bank to itself.

The builder creates the directory for us. If two names have exactly the same
contents, both can point to the same stored copy. These are PROGRAM files;
this ROM format doesn't store types such as DIS/VAR 80.

For someone reading the code, this format is called **CF01**. Bank zero has
`CF01` at offset `>0010`, the file count at `>0014`, and the directory at
`>0020`. Each directory entry is just 16 bytes:

```text
Name (10 bytes) | File size (2) | Starting bank (2) | Offset in bank (2)
```

Names are padded with spaces, and the two-byte numbers have their high byte
first. File contents start after bank zero, on even byte offsets.

### UBE1: small blocks shared by all the saved files

The EEPROM is only 4K, and part of it belongs to UberGROM. We divide the space
that's left into small, 32-byte blocks. A file uses as many blocks as it needs,
plus some blocks describing the file.

```text
4K EEPROM
  [ UberGROM configuration - leave this alone ]
  [ Directory A ][ Directory B ]
  [ 118 blocks shared by file descriptions and file contents ]

Current directory
  PIRATE -> file description -> blocks holding the saved game
  MYBASIC -> file description -> blocks holding the BASIC program
```

A file description holds its name, type, size and the list of blocks containing
its data. For record files it also holds the record information, so UBE1 can
tell a PROGRAM file from something like DIS/FIX 128 or DIS/VAR 80. The blocks
for a file don't have to sit next to each other.

For example, **suppose a saved game is 192 bytes**. That's an illustration,
not a limit or a claim about every Adventure save:

| What it needs | Space used |
| --- | --- |
| The 192 bytes of saved-game data | 6 blocks |
| Its file description, including the block list | 2 blocks |
| Total | 8 blocks, or 256 bytes |

On an otherwise empty UBE1, that leaves 110 blocks free. A larger save uses
more blocks; we don't reserve a fixed 192-byte slot for every file. There are
up to 16 directory entries, but all the files share the available space. The
largest raw file is 3,616 bytes, including neither its description nor the
directory in that figure.

When we replace a save, we write its new contents into free blocks first,
then switch the directory to the new version. That's why replacing a file
needs spare space even if its size hasn't changed. Once that succeeds, the
old blocks can be reused. If there's no room, we return a disk-full error;
we don't delete somebody's older save to make room.

The two directories let us make that switch last. The code checks the
directory and file descriptions, and writes the CRC check values required by
the **UBF1** format. It doesn't repeatedly checksum every file, and it can't
guarantee recovery from every electrical failure.

For the exact EEPROM layout, `>0000->0101` is UberGROM's configuration,
`>0102->013F` holds the two 31-byte directories, and `>0140->0FFF` holds the
118 blocks. These are offsets within EEPROM, not GROM addresses.

### Loading an adventure and saving your place

`ROM1.PIRATE` is the adventure itself. `UBE1.PIRATE` is your saved position.
They can have the same name because they're on different devices. Saving your
place changes UBE1; the adventure in ROM1 stays as it was built.

There's a small `2026 Hexbus` signature at offset `>1FDC` in the UBE1 GROM.
It uses 11 bytes at the end and doesn't run or appear on screen. If you use
this GROM in another project, I ask that you leave it there so people know
where it came from.
