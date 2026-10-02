from pathlib import Path
import hashlib
import json
import tempfile
import zipfile
import subprocess
ROOT=Path(__file__).resolve().parents[1]
reports=json.loads((ROOT/'downloads/SHA256.json').read_text())
assert len({row['sha256'] for row in reports.values()})==2
for name,row in reports.items():
    path=ROOT/'downloads'/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    with tempfile.TemporaryDirectory() as directory:
        folder=Path(directory)
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            assert all(not n.startswith(('/', '..')) and '..' not in Path(n).parts for n in archive.namelist())
            archive.extractall(folder)
        if 'CopyPaste' in name:
            rows=json.loads((ROOT/'manifest.json').read_text())
            expected={r['path'] for r in rows}|{'START-HERE.txt','PATCH-FILES-SHA256.json','licenses/SeochoBatang-OFL.txt'}
            assert {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}==expected
            for row in rows:
                assert hashlib.sha256((folder/row['path']).read_bytes()).hexdigest()==row['patched_sha256']
            assert not any(p.suffix.lower() in ('.exe','.py','.ps1','.bat','.cmd') for p in folder.rglob('*'))
            assert len(rows)==33
            continue
        assert (folder/row['entry_point']).read_bytes()==(ROOT/'CockspurKoreanPatcher.exe').read_bytes()
        for payload in ('patches','runtime','licenses'):
            for original in (ROOT/payload).rglob('*'):
                if original.is_file():
                    expected_bytes=original.read_bytes();actual_bytes=(folder/original.relative_to(ROOT)).read_bytes()
                    if payload=='licenses':expected_bytes=expected_bytes.replace(b'\r\n',b'\n');actual_bytes=actual_bytes.replace(b'\r\n',b'\n')
                    assert expected_bytes==actual_bytes
        report=folder/'ui.json'
        result=subprocess.run([str(folder/row['entry_point']),'--smoke-ui',str(report)])
        if result.returncode:
            raise RuntimeError(report.read_text(encoding='utf-8') if report.exists() else 'Executable initialization failed')
        ui=json.loads(report.read_text(encoding='utf-8'))
        assert ui['tk_initialized'] and ui['controls']==(3 if 'CopyPaste' in name else 5)
        assert not any(p.name in ('files','original-files') for p in folder.rglob('*'))
print('Both ZIPs: hashes and clean extraction passed; quick installer UI passed; copy ZIP contains exactly 33 ready-to-copy game files and no setup program')
