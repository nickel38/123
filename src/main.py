"""Точка входа эмулятора варианта 22."""

import argparse

from .shell import Shell
from .vfs import VFS


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Эмулятор оболочки, вариант 22")
    parser.add_argument("--vfs", default="fixtures/multiple.json", help="путь к JSON VFS")
    parser.add_argument("--script", default="", help="путь к стартовому сценарию")
    return parser.parse_args()


def main() -> int:
    args = read_args()
    config = {"vfs": args.vfs, "script": args.script}
    try:
        vfs = VFS(args.vfs)
        shell = Shell(vfs, config)
        shell.conf_dump([])
        vfs.show_motd()
        if args.script and not shell.run_script(args.script):
            return 1
        shell.repl()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Ошибка запуска: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
