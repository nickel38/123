import json
import tempfile
import unittest
from pathlib import Path

from src.vfs import VFS


class VFSTests(unittest.TestCase):
    def make_vfs(self, data):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "vfs.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return VFS(path)

    def test_text_and_base64(self):
        vfs = self.make_vfs({"name": "x", "directories": ["/", "/d"],
                             "files": {"/a": {"text": "текст"},
                                       "/d/b": {"base64": "AAE="}}})
        self.assertEqual(vfs.files["/a"], "текст".encode())
        self.assertEqual(vfs.files["/d/b"], b"\x00\x01")

    def test_paths_and_listing(self):
        vfs = self.make_vfs({"name": "x", "directories": ["/", "/d"],
                             "files": {"/d/a": {"text": ""}, "/.h": {"text": ""}}})
        self.assertEqual(vfs.resolve("../d", "/d"), "/d")
        self.assertEqual(vfs.list_names("/d"), ["a"])
        self.assertEqual(vfs.list_names("/", True), [".", "..", ".h", "d"])

    def test_remove_protection(self):
        vfs = self.make_vfs({"name": "x", "directories": ["/", "/d"],
                             "files": {"/d/a": {"text": ""}}})
        with self.assertRaises(ValueError):
            vfs.remove("/", True, "/")
        with self.assertRaises(ValueError):
            vfs.remove("/d", True, "/d")


if __name__ == "__main__":
    unittest.main()
