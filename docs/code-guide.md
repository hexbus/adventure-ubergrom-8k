<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# How the small cartridge service works

The source is TI **Graphics Programming Language (GPL)**. The original Adventure
interpreter loads a PROGRAM file through ROM1 and saves through UBE1. The two
devices share the cartridge but have different jobs.

| Source | Responsibility |
| --- | --- |
| [rom1.gpl](../sources/gpl/rom1/rom1.gpl) | Read-only PROGRAM loader; finds a filename and copies its banked-ROM bytes into the caller's VDP buffer |
| [ube1.gpl](../sources/gpl/ubf1-compact/ube1.gpl) | GROM header, request dispatch, filesystem mount, allocation, PROGRAM operations and EEPROM writes |
| [records.gpl](../sources/gpl/ubf1-compact/records.gpl) | One open file, record positions and the staged record buffer |
| [directory.gpl](../sources/gpl/ubf1-compact/directory.gpl) | Catalog entries and free allocation-block count |
| [manager.gpl](../sources/gpl/ubf1-compact/manager.gpl) | SAVED GAMES menu, marks, copy and delete |
| [basic-cat.gpl](../sources/gpl/ubf1-compact/basic-cat.gpl) | BASIC CALL CAT, using the shared catalog/display routines |
| [scratch.gpl](../sources/gpl/ubf1-compact/scratch.gpl) | Small shared scratch/descriptor helpers |

## A file request

The console finds the device's GROM header and passes a **PAB**, the file request
block, in VDP memory. UBE1 saves the caller's GROM base, uses private base 14,
checks the configuration and mounts the directory. It then performs the requested
operation, reports a TI error if necessary, relocks EEPROM, restores the caller
base and returns through the console. It never formats a volume implicitly.

PROGRAM LOAD/SAVE transfer a whole file. Record OPEN stages a file in a
3,616-byte buffer; READ/WRITE work on that buffer and CLOSE commits changes.
The menu submits normal file requests instead of editing EEPROM itself.
CALL CAT saves/restores BASIC's screen and scratch so the caller can continue.

## Where things live

| View / address | Contents |
| --- | --- |
| Base 0, `>6000->7FFF` | Adventure's original 6K plus the 318-byte ROM1 loader |
| Base 1, `>6000->7FFF` | The same Flash page; matching headers suppress REVIEW MODULE LIBRARY |
| Base 0, `>8000->9FFF` | Frozen UBE1 service, manager, CALL CAT and signature |
| Base 14, `>6000` | Working RAM; 5,632 bytes reserved |
| Base 14, `>8000` | The same UBE1 code page |
| Bases 0 and 14, `>A000->AFFF` | EEPROM |
| Base 15 | Firmware configuration/unlock interface |

A base selects a view through a different GROM port; an address selects a
location inside that view. This is separate from U2's positive-switched 8K
CPU-ROM banks. The table documents this frozen Adventure profile, not a promise
that these addresses can coexist with every other module.

## Two small filesystems

**ROM1 / CF01:** bank zero holds `CF01` at offset `>0010`, a big-endian file
count at `>0014`, and 16-byte entries from `>0020`. Each entry contains a
10-byte space-padded name, 2-byte length, 2-byte bank and 2-byte bank offset.
Payloads begin after bank zero, with two-byte alignment. Identical payloads
can share an offset. This frozen format stores PROGRAM data, not record types.

**UBE1 / UBF1:** EEPROM `>0000->0101` is firmware configuration. Two 31-byte
directory roots occupy `>0102->013F`. The remaining `>0140->0FFF` holds 118
allocation blocks of 32 bytes, used for file metadata and data. Up to 16 files
fit, subject to space. The maximum raw file is 3,616 bytes; replacing it needs
additional free blocks. There is no automatic FIFO deletion.

Saving checks capacity, writes new blocks without overwriting the active file,
and publishes the replacement directory last with its commit byte. The compact
reader checks directory/descriptor integrity but does not repeatedly checksum
every payload. CRC writing keeps UBF1 compatibility. This is a practical small
store, not a promise of recovery from every electrical failure.

The unreferenced `2026 Hexbus` signature is at offset `>1FDC` of the UBE1 GROM.
No code branches to it. Comments can be improved while the rebuild check keeps
every assembled byte identical to the frozen image.
