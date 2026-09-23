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

## The ROM directory and save directory

**ROM1 uses CF01.** Bank zero has `CF01` at offset `>0010`, a big-endian file
count at `>0014`, and 16-byte directory entries starting at `>0020`. Each entry
has a 10-byte name padded with spaces, followed by a 2-byte length, 2-byte bank
number and 2-byte offset in that bank.

The file data starts after bank zero and is aligned to two bytes. If two files
have exactly the same data, they can share a copy. This version of ROM1 holds
PROGRAM files; it doesn't store record-file types.

**UBE1 uses UBF1.** We leave EEPROM `>0000->0101` for UberGROM's configuration.
Two 31-byte directory roots use `>0102->013F`. The rest, `>0140->0FFF`, gives us
118 blocks of 32 bytes for file information and data.

There's room for up to 16 files if the data fits. The largest raw file is
3,616 bytes, and replacing a file needs additional free blocks. We don't throw
away the oldest save when it fills up. You decide what to delete.

On a save, we check that there's room, write the new blocks, and make the new
directory current last by writing its commit byte. The old file stays in place
until then. The compact reader checks the directory and file descriptors;
it doesn't keep checksumming every file. We still write the CRCs needed for
UBF1 compatibility. This doesn't guarantee recovery from every electrical failure.

The `2026 Hexbus` signature sits at offset `>1FDC` in the UBE1 GROM. Nothing
executes it. We can improve the comments and directions while checking that
the assembled bytes stay exactly the same.
