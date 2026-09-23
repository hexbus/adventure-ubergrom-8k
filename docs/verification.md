<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# What we froze and checked

We're keeping this Adventure version as it is: the 8K UBE1 GROM with the
`2026 Hexbus` signature, the 318-byte ROM1 loader, and the blank EEPROM with
the corrected GROM mapping. Their sizes and hashes are in
[release/frozen.json](../release/frozen.json). The original freeze is tagged
`adventure-8k-frozen-2026-09-23`.

## What works so far

On my hardware, I've loaded an adventure, saved a game and loaded that save
back up. Copying a file within UBE1 and deleting one from TI BASIC work too.
The mapping fix gets rid of REVIEW MODULE LIBRARY.

We also ran emulator and host tests for Adventure save/restore, BASIC PROGRAM
and record files, catalogs, menu copy/delete, full-storage errors, and keeping
writes out of UberGROM's protected configuration. The signature-only change
passed those checks. This doesn't mean we've tested every hardware setup or
what happens with every possible power failure.

To check the new builder, we rebuilt both of our existing adventure collections.
All the programming images matched the signed reference byte for byte. We also
built the WHTech PIRATE example from the [build directions](building.md).
There's a short [verification summary](../release/verification.json) with the
release files.

## Check your copy

From the repository directory, run:

```powershell
python tests/verify.py
```

This checks the finished components and exercises the ROM packer with made-up
files. It checks files that cross ROM-bank boundaries, names sharing the same
data, bad inputs, and attempts to overwrite protected output paths.

If you have xdt99, you can also assemble the source and check that it produces
the exact same UBE1 GROM and ROM1 loader:

```powershell
python tests/verify.py --xdt99 E:/git/xdt99
```

Use the path to your own xdt99 directory. These checks don't need any adventure
files, the original Adventure GROM, or the AVR firmware.

Once you've programmed a cartridge, follow the load/save/restart check in the
[programming directions](programming.md). That checks your assembled cartridge
as well as the files used to build it.
