import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from patcher_engine import Patcher
from test_prepare import fixture


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.package, self.game = self.root / 'package', self.root / 'game'
        self.package.mkdir()
        self.game.mkdir()
        self.original, self.patched, self.extra = b'abc', b'acc!', b'localized image fixture'
        delta = fixture([3, 1, 0], bytes([0, 1, 0]), b'!', 4)
        (self.package / 'change.bsdiff').write_bytes(delta)
        (self.package / 'new.dat').write_bytes(self.extra)
        (self.game / 'data.bin').write_bytes(self.original)
        digest = lambda b: hashlib.sha256(b).hexdigest()
        rows = [{'path': 'data.bin', 'original_sha256': digest(self.original), 'patched_sha256': digest(self.patched), 'payload': 'change.bsdiff', 'payload_sha256': digest(delta)}, {'path': 'added.dat', 'new_file': True, 'original_sha256': None, 'patched_sha256': digest(self.extra), 'payload': 'new.dat', 'payload_sha256': digest(self.extra)}]
        (self.package / 'manifest.json').write_text(json.dumps(rows))
        self.engine = Patcher(self.package, self.game)

    def tearDown(self):
        self.temp.cleanup()

    def test_install_restore_reinstall(self):
        self.engine.install()
        self.assertEqual(self.engine.verify(), 'installed')
        self.engine.restore()
        self.assertEqual(self.engine.verify(), 'original')
        self.engine.install()
        self.engine.restore()
        self.assertEqual((self.game / 'data.bin').read_bytes(), self.original)

    def test_unknown_modification_preserved(self):
        (self.game / 'data.bin').write_bytes(b'user changed this')
        with self.assertRaises(ValueError):
            self.engine.install()
        self.assertFalse(self.engine.backup.exists())

    def test_existing_extra_file_preserved(self):
        (self.game / 'added.dat').write_bytes(b'user data')
        with self.assertRaises(ValueError):
            self.engine.install()
        self.assertEqual((self.game / 'added.dat').read_bytes(), b'user data')

    def test_corrupt_backup_blocks_restore(self):
        self.engine.install()
        self.engine.original(self.engine.rows[0]).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            self.engine.restore()
        self.assertEqual(self.engine.verify(), 'installed')

    def test_failed_second_write_rolls_back(self):
        original_replace = self.engine.replace
        calls = [0]
        def fail_once(source, target, expected):
            calls[0] += 1
            if calls[0] == 2:
                raise OSError('simulated disk failure')
            return original_replace(source, target, expected)
        self.engine.replace = fail_once
        with self.assertRaises(OSError):
            self.engine.install()
        self.assertEqual(self.engine.verify(), 'original')
        self.assertEqual(json.loads(self.engine.state.read_text())['status'], 'rolled_back')

    def test_manual_install_not_claimed_as_restorable(self):
        (self.game / 'data.bin').write_bytes(self.patched)
        (self.game / 'added.dat').write_bytes(self.extra)
        with self.assertRaises(ValueError):
            self.engine.restore()

    def test_export_preserves_game_and_provides_backup(self):
        output = self.root / 'copy-files'
        self.engine.export_copy(output)
        self.assertEqual(self.engine.verify(), 'original')
        self.assertFalse(self.engine.backup.exists())
        self.assertEqual((output / 'files/data.bin').read_bytes(), self.patched)
        self.assertEqual((output / 'files/added.dat').read_bytes(), self.extra)
        self.assertEqual((output / 'original-files/data.bin').read_bytes(), self.original)
        self.assertEqual((output / 'added-files.txt').read_text().strip(), 'added.dat')

    def test_export_does_not_overwrite_existing_folder(self):
        output = self.root / 'copy-files'
        output.mkdir()
        (output / 'user.txt').write_text('preserve')
        with self.assertRaises(ValueError):
            self.engine.export_copy(output)
        self.assertEqual((output / 'user.txt').read_text(), 'preserve')

    def test_export_rejects_game_folder_destination(self):
        with self.assertRaises(ValueError):
            self.engine.export_copy(self.game / 'copy-files')
        self.assertFalse((self.game / 'copy-files').exists())

    def test_export_rejects_corrupt_payload_without_partial_output(self):
        (self.package / 'change.bsdiff').write_bytes(b'corrupt')
        output = self.root / 'copy-files'
        with self.assertRaises(ValueError):
            self.engine.export_copy(output)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
