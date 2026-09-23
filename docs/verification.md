<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Frozen release and verification

`adventure-8k-frozen-2026-09-23` preserves the signed 8K Adventure service with
the corrected GROM mapping. The three public assets and their hashes are in
[release/frozen.json](../release/frozen.json). Do not overwrite these assets.

User reports confirm Adventure loading, save/restore, UBE1 file copy, BASIC
DELETE and the disappearance of REVIEW MODULE LIBRARY. The signature-only
change passed emulator/host checks; these reports do not establish exhaustive
hardware acceptance or power-loss behavior.

The development build's acceptance suite exercised Adventure save/restore,
BASIC PROGRAM and record I/O, catalog, manager copy/delete, space/error cases,
configuration protection and packaging. Full research evidence and original
inputs remain in the development workspace and the ignored local reference.
They are intentionally excluded from the public source export.

## Check this repository

```powershell
python tests/verify.py
python tests/verify.py --xdt99 E:/git/xdt99
```

The first command checks frozen assets and synthetic file packing, cross-bank
reads, aliases, input validation and output protection. The second also
assembles the commented sources and compares their bytes to the frozen GROM
and ROM1 loader. It needs no Adventure databases, original GROM or AVR firmware.

Private integration verification rebuilt both existing collections with the
new user-input builder and compared every programming image to the signed
reference. It also checked the documented WHTech input example. This evidence
is recorded locally, without putting the inputs in Git or the public export.

## Prepare a GitHub directory

```powershell
python tools/prepare_release.py
```

The exporter copies only the files listed in `public-files.json`, checks them
against `freeze-manifest.json`, and writes a fresh `github-release/` directory
with a sibling ZIP under `output/`. It refuses an existing staging directory.
It never copies local inputs, private reference images, Git history or custom
cartridges. Publishing is a separate step; this command does not use GitHub.

Keep future ToD and printer/cassette work in the development repository.
This repository's runtime is finished; changes here should explain or package
the same frozen bytes rather than add features.
