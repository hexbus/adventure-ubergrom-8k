<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# What we froze and checked

This is the signed 8K Adventure version, with the mapping fix that removes
REVIEW MODULE LIBRARY. Its tag is `adventure-8k-frozen-2026-09-23`.
The three finished components and their hashes are listed in
[release/frozen.json](../release/frozen.json). We're keeping those bytes as-is.

On my hardware, Adventure loads and saves, saved games load back up, files copy
within UBE1, and BASIC DELETE works. The mapping fix also gets rid of REVIEW
MODULE LIBRARY. The signature-only change passed the emulator and host checks.
That doesn't mean every hardware combination or power failure has been tested.

The development tests covered Adventure save/restore, BASIC PROGRAM and record
files, catalogs, menu copy/delete, full-storage and error cases, protection of
the configuration area, and the generated programming files. The detailed
research and original inputs stay in the development workspace and our private
reference copy. They aren't part of the public download.

## Check your copy

```powershell
python tests/verify.py
python tests/verify.py --xdt99 E:/git/xdt99
```

The first command checks the frozen files and tries the packer with made-up test
data. That includes files crossing ROM-bank boundaries, duplicate data, bad
inputs and attempts to overwrite protected output paths.

The second command also assembles the source and compares it with the finished
UBE1 GROM and ROM1 loader. Change the xdt99 path to yours. Neither test needs
the original Adventure GROM, adventure files or AVR firmware.

We also used the new builder to recreate both of our existing adventure
collections. Every programming image matched the signed reference byte for
byte. The WHTech example built successfully too. Those checks used private
inputs, which stay out of Git and the public release copy.

## Make the GitHub copy

```powershell
python tools/prepare_release.py
```

This makes `github-release/` and a ZIP under `output/`. It takes only the files
in `public-files.json` and checks them against `freeze-manifest.json` first.
The manifest covers the docs as well as the code, so a documentation update
needs its recorded hashes refreshed before exporting.

It won't overwrite a previous export. Keep the old one and export from a fresh
checkout, or move the old directory and ZIP aside first. Private inputs, old
cartridges and Git history aren't included. This command doesn't publish
anything to GitHub.

The original freeze tag stays put when we update the wording. Future ToD and
printer/cassette work belongs in the development repo. The Adventure code here
is the finished version; the comments and directions can still get clearer.
