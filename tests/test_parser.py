import unittest
from src.parser import parse_command, parse_options


class ParserTests(unittest.TestCase):
    def test_quotes_and_comments(self):
        self.assertEqual(parse_command('ls "my folder" # comment'), ["ls", "my folder"])

    def test_combined_options(self):
        self.assertEqual(parse_options(["-rf", "--", "-name"], "rRf"), ({"r", "f"}, ["-name"]))

    def test_bad_quote(self):
        with self.assertRaises(ValueError):
            parse_command('cd "unfinished')


if __name__ == "__main__":
    unittest.main()
