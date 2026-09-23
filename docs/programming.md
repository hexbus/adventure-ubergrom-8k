<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Using and programming the cartridge

## Load an adventure and save a game

Select **ADVENTURE** and enter `ROM1.MYGAME`, using one of the names in your
`rom-map.txt`. Answer **N** to start a new game.

When you want to save, type **SAVE GAME** and enter something like
`UBE1.MYSAVE`. To pick up where you left off, load the same adventure, answer
**Y**, and enter that saved filename. You don't need quotes at these prompts.

## What's on the cartridge?

Select **SAVED GAMES** from the menu. You can see what's there, mark files to
delete, or copy them somewhere else.

| Key | What it does |
| --- | --- |
| E / S or up/down arrows | Move through the 16 entries |
| D | Mark a file to delete; press again to unmark it |
| C | Mark a file to copy; press again to unmark it |
| X | Do the marked actions |
| Enter | Go back to the title screen; any remaining marks are discarded |

Copy asks where you want the file to go. You can enter `UBE1.MYSAVE2`,
`DSK1.MYSAVE`, or `CS1`. You'll need a disk system or cassette recorder for
those last two. Copy leaves the original alone, but it may replace a file
already at the destination. A blank answer cancels.

When the save area is full, nothing gets deleted for you. Pick something you
no longer need and delete it. Replacing a save needs some free space too.
A `!` beside a file means it's protected.

You can also do this from TI BASIC:

```basic
CALL CAT("ROM1")
CALL CAT("UBE1")
DELETE "UBE1.MYSAVE2"
```

PROGRAM files work, as do DISPLAY and INTERNAL files with FIXED or VARIABLE
records. The DSR handles one open record file at a time.

The printer and CS1 redirection ideas aren't in this version. Copying to a
real cassette still works through the console's normal CS1 device.

## Program a new cartridge

First, [build your files](building.md). The directions below are for a new
cartridge with an empty save area. If you've already been using the cartridge,
read and back up its EEPROM first. Our blank EEPROM file won't keep your saves.

| Chip / memory | File | Size / starting address |
| --- | --- | --- |
| U2 adventure ROM | `adventure-rom512k.bin` | 512 KiB / 0 |
| U3 ATmega1284P Flash | `adventure-ubergrom-flash-atmega1284p.bin` | 128 KiB / 0 |
| U3 ATmega1284P EEPROM | `adventure-ubergrom-eeprom-atmega1284p.bin` | 4 KiB / 0 |

Choose the part number that's actually on your U2 chip, and ATmega1284P for
U3. Load each file into its matching memory area, program it, and run Verify.
There's no byte swapping or bank reversal to do.

Set and read back the fuses: **LOW C2, HIGH D8, EXTENDED FF**. The image files
don't set those for you. Remember that with D8, a chip erase also erases EEPROM.

There's also a 132K combined file,
`adventure-ubergrom-whole-atmega1284p.bin`. It puts Flash at
`0x00000-0x1FFFF` and EEPROM at `0x20000-0x20FFF`. Use it only if your programmer
understands that layout. Don't load the whole thing as Flash. The build also
makes Intel HEX files for the two separate memories.

Leave the configuration write-protect jumper on for normal use. UBE1 can still
save files; it stays out of the protected configuration area.

Once it's installed, load a game, save to `UBE1.TEST`, restart and load that
save back up. Then delete TEST from the menu or BASIC.
