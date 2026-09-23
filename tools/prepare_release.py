# Copyright (c) 2026 hexbus.
# SPDX-License-Identifier: Apache-2.0
"""Export only the reviewed, hash-pinned public files; no Git or network access."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    names = json.loads((ROOT/'public-files.json').read_text())['files']
    frozen = json.loads((ROOT/'freeze-manifest.json').read_text())
    if set(names) != set(frozen['files']) or len(names) != len(set(names)):
        raise ValueError('Public file list differs from the reviewed freeze manifest')
    # Validate the whole set before creating output. Never glob the workspace.
    for name in names:
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] in {
                '.git', 'output', 'local-inputs', 'local-reference', 'github-release'}:
            raise ValueError('Private or unsafe export path: '+name)
        file = ROOT/name
        if not file.resolve().is_relative_to(ROOT) or file.is_symlink():
            raise ValueError('Export must use regular files inside the repository')
        data = file.read_bytes()
        expected = frozen['files'][name]
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError('Frozen public file changed: '+name)
    target = ROOT/'github-release'
    archive = ROOT/'output/adventure-ubergrom-8k-source.zip'
    if target.exists() or archive.exists():
        raise ValueError('Staging or ZIP already exists; retain it and use a fresh checkout to export again')
    target.mkdir()
    for name in names+['freeze-manifest.json']:
        destination = target/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, destination)
    archive.parent.mkdir(exist_ok=True)
    with ZipFile(archive, 'x', ZIP_DEFLATED) as output:
        for name in names+['freeze-manifest.json']:
            output.write(target/name, name)
    with ZipFile(archive) as check:
        assert check.testzip() is None
        assert set(check.namelist()) == set(names)|{'freeze-manifest.json'}
        for name in check.namelist():
            assert check.read(name) == (target/name).read_bytes()
    print('Prepared '+str(target))
    print('ZIP: '+str(archive))
    print('No original Adventure module, adventure databases or AVR firmware included.')


if __name__ == '__main__':
    prepare()
