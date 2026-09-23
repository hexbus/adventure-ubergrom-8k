<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Use and program Adventure UberGROM

## Play and save

Select **ADVENTURE**. Enter `ROM1.MYGAME`, using a name from your build's
`rom-map.txt`. Answer **N** for a new game. During play, type **SAVE GAME** and
enter `UBE1.MYSAVE`. To restore, load the same adventure, answer **Y**, and enter
that saved filename. Adventure's prompts need no quotes.

Select **SAVED GAMES** to manage files:

| Key | Action |
| --- | --- |
| E / S or up/down arrows | Move through the 16 entries |
| D | Toggle a deletion mark |
| C | Toggle a copy mark |
| X | Execute marked actions |
| Enter | Return to the title screen without executing remaining marks |

Copy asks for a destination, such as `UBE1.MYSAVE2`, `DSK1.MYSAVE`, or `CS1`.
A disk or cassette destination needs the corresponding equipment. Copy keeps
the source but may replace an existing destination. Empty input cancels.
Nothing is deleted automatically when storage is full. Replacement needs
spare space; delete unwanted files if necessary. `!` marks a protected file.

TI BASIC also supports:

```basic
CALL CAT("ROM1")
CALL CAT("UBE1")
DELETE "UBE1.MYSAVE2"
```

PROGRAM and DISPLAY/INTERNAL FIXED/VARIABLE files are supported, with one open
record file at a time. Printer and CS1 redirection are not included. Copy to
the normal cassette device is a separate existing operation.

## Program a new cartridge

Build your images first using the [build guide](building.md). These directions
assume an empty save area. Read and retain existing EEPROM before reprogramming;
the supplied blank EEPROM does not contain your saves.

| Chip / memory | Generated file | Size / start |
| --- | --- | --- |
| U2 adventure ROM | `adventure-rom512k.bin` | 512 KiB / 0 |
| U3 ATmega1284P Flash | `adventure-ubergrom-flash-atmega1284p.bin` | 128 KiB / 0 |
| U3 ATmega1284P EEPROM | `adventure-ubergrom-eeprom-atmega1284p.bin` | 4 KiB / 0 |

Choose the actual U2 chip model and ATmega1284P in your programmer. Do not swap
bytes or reverse banks. Program the matching memory regions and verify them.
Set/read back fuses **LOW C2, HIGH D8, EXTENDED FF**. Image files do not set
fuses. With D8, a chip erase also erases EEPROM.

The combined `adventure-ubergrom-whole-atmega1284p.bin` is 132 KiB: Flash at
`0x00000-0x1FFFF`, then EEPROM at `0x20000-0x20FFF`. Use it only with a programmer
that supports that combined buffer layout; never load it as Flash alone.
Equivalent Intel HEX files are also produced for the separate memories.

Keep the configuration write-protect jumper fitted in normal use. UBE1 writes
its save area without altering the protected configuration. After installation,
load a game, save to `UBE1.TEST`, restart, restore it and delete TEST.
