import bz2
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('prepare', Path(__file__).resolve().parents[1] / 'tools/prepare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def integer(n):
    return (abs(n) | ((1 << 63) if n < 0 else 0)).to_bytes(8, 'little')


def fixture(controls, differences, extra, size):
    ctrl = bz2.compress(b''.join(integer(n) for n in controls))
    diff = bz2.compress(differences)
    return b'BSDIFF40' + integer(len(ctrl)) + integer(len(diff)) + integer(size) + ctrl + diff + bz2.compress(extra)


class PrepareTests(unittest.TestCase):
    def test_add_copy_and_extra(self):
        delta = fixture([3, 1, 0], bytes([0, 1, 0]), b'!', 4)
        self.assertEqual(module.patch(b'abc', delta), b'acc!')

    def test_negative_seek(self):
        delta = fixture([3, 0, -3, 3, 0, 0], bytes(6), b'', 6)
        self.assertEqual(module.patch(b'abc', delta), b'abcabc')

    def test_truncated_control_rejected(self):
        with self.assertRaises(ValueError):
            module.patch(b'a', fixture([1], b'a', b'', 1))

    def test_oversize_control_rejected(self):
        with self.assertRaises(ValueError):
            module.patch(b'a', fixture([2, 0, 0], b'aa', b'', 1))

    def test_wrong_header(self):
        with self.assertRaises(ValueError):
            module.patch(b'a', b'not a delta')

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            module.contained(Path('safe'), '../elsewhere')


if __name__ == '__main__':
    unittest.main()
