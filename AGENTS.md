# Frozen Adventure 8K project

This repository is the finished Adventure cartridge, not the development home
for ToD, printer/cassette redirection or new filesystem features. Keep the
frozen runtime byte-identical to release/frozen.json. Comments and usage
documentation may improve without changing the generated GROM.

Never commit local-inputs/, local-reference/, output/ or github-release/.
They may contain user-supplied adventures or original module/firmware images.
Create GitHub staging only with tools/prepare_release.py, which uses an explicit
public-file list. Never export a whole working directory or local Git history.

README.md and docs/ are authoritative. Keep explanations short and link to
details. Preserve evidence labels; an emulator result is not a hardware test.
After changing user-facing Markdown, regenerate its PDF with
`powershell -ExecutionPolicy Bypass -File tools/build-docs.ps1 -Path <file>`.
Inspect rendered pages before presenting a PDF. Never edit generated PDFs.
