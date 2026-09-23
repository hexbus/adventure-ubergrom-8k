<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Updating the docs and preparing a release

The Adventure code here is finished. We can make the directions and comments
clearer, but the assembled bytes must still match `release/frozen.json`.
Leave the original freeze tag in place. ToD and the printer/cassette work belong
in the development repository.

After changing a Markdown guide, rebuild its PDF:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build-docs.ps1 -Path docs/verification.md
```

If you change source comments, use the source rebuild check in
[verification.md](verification.md) to make sure the assembled bytes haven't changed.

## Prepare the files for GitHub

`public-files.json` lists what belongs in the public copy. `freeze-manifest.json`
records the size and SHA-256 of each of those files, including the docs. After
reviewing a documentation change, update its recorded size and hash. Add a new
public guide to both lists if needed. Don't change a binary's expected hash to
make a failing check pass.

Then run:

```powershell
python tools/prepare_release.py
```

This checks the listed files, copies them to `github-release/`, and creates
`output/adventure-ubergrom-8k-source.zip`. It doesn't publish to GitHub.

The exporter won't overwrite an earlier copy. Move the previous directory and
ZIP aside first, or export from a fresh checkout. Keep private inputs, old
cartridge images and Git history out of the public package.
