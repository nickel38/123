import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS


class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / "vfs.json"
        path.write_text('{"name":"x","directories":["/","/d"],"files":{"/d/a":{"text":"a"}}}', encoding="utf-8")
        self.shell = Shell(VFS(path), {"vfs": str(path), "script": ""})

    def output(self, line):
        stream = io.StringIO()
        with redirect_stdout(stream):
            ok = self.shell.execute(line)
        return ok, stream.getvalue()

    def test_navigation_and_listing(self):
        ok, _ = self.output("cd /d")
        self.assertTrue(ok)
        self.assertEqual(self.shell.cwd, "/d")
        ok, text = self.output("ls")
        self.assertTrue(ok)
        self.assertEqual(text.strip(), "a")

    def test_rm_and_exit(self):
        ok, _ = self.output("rm a")
        self.assertFalse(ok)
        ok, _ = self.output("cd /d")
        self.assertTrue(ok)
        ok, _ = self.output("rm a")
        self.assertTrue(ok)
        self.assertNotIn("/d/a", self.shell.vfs.files)
        ok, _ = self.output("exit")
        self.assertTrue(ok)
        self.assertFalse(self.shell.running)


if __name__ == "__main__":
    unittest.main()
