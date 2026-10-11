"""Команды оболочки, сценарии и интерактивный REPL."""

import time
from datetime import datetime, timedelta
from pathlib import Path

from .parser import one_path, parse_command, parse_options, require_no_args
from .vfs import VFS


class Shell:
    def __init__(self, vfs: VFS, config: dict[str, str] | None = None):
        self.vfs = vfs
        self.name = vfs.name
        self.cwd = "/"
        self.running = True
        self.config = config or {"vfs": "", "script": ""}
        self.started = time.monotonic()
        self.commands = {
            "ls": self.ls, "cd": self.cd, "pwd": self.pwd,
            "date": self.date, "uptime": self.uptime,
            "rm": self.rm, "conf-dump": self.conf_dump, "exit": self.exit,
        }

    def prompt(self) -> str:
        return f"{self.name}:{self.cwd}$ "

    def execute(self, line: str) -> bool:
        try:
            words = parse_command(line)
            if not words:
                return True
            command, *args = words
            if command not in self.commands:
                raise ValueError(f"неизвестная команда: {command}")
            self.commands[command](args)
            return True
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
            return False

    def ls(self, args: list[str]) -> None:
        flags, paths = parse_options(args, "a")
        path = self.vfs.resolve(one_path(paths, self.cwd), self.cwd)
        for name in self.vfs.list_names(path, "a" in flags):
            print(name)

    def cd(self, args: list[str]) -> None:
        path = self.vfs.resolve(one_path(args, "/"), self.cwd)
        self.vfs.require_directory(path)
        self.cwd = path

    def pwd(self, args: list[str]) -> None:
        require_no_args(args, "pwd")
        print(self.cwd)

    def date(self, args: list[str]) -> None:
        require_no_args(args, "date")
        print(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"))

    def uptime(self, args: list[str]) -> None:
        require_no_args(args, "uptime")
        print(f"up {timedelta(seconds=int(time.monotonic() - self.started))}")

    def rm(self, args: list[str]) -> None:
        flags, paths = parse_options(args, "rRf")
        if not paths and "f" not in flags:
            raise ValueError("rm: укажите хотя бы один путь")
        recursive = bool({"r", "R"} & flags)
        for value in paths:
            try:
                path = self.vfs.resolve(value, self.cwd)
                self.vfs.remove(path, recursive, self.cwd)
            except FileNotFoundError:
                if "f" not in flags:
                    raise

    def conf_dump(self, args: list[str]) -> None:
        require_no_args(args, "conf-dump")
        for key, value in self.config.items():
            print(f"{key}={value}")

    def exit(self, args: list[str]) -> None:
        require_no_args(args, "exit")
        self.running = False

    def run_script(self, path: str) -> bool:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            print(self.prompt() + line)
            if not self.execute(line):
                print(f"Скрипт остановлен: строка {number}")
                return False
        return True

    def repl(self) -> None:
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue
            self.execute(line)
