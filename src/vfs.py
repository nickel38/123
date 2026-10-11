"""Виртуальная файловая система, загружаемая из JSON."""

import base64
import json
import posixpath
from pathlib import Path


class VFS:
    """Хранит каталоги и байты файлов в памяти."""

    def __init__(self, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.name = data["name"]
        self.directories = set(data["directories"])
        self.files: dict[str, bytes] = {}
        for name, content in data["files"].items():
            if "text" in content:
                self.files[name] = content["text"].encode("utf-8")
            elif "base64" in content:
                self.files[name] = base64.b64decode(content["base64"], validate=True)
            else:
                raise ValueError(f"VFS: у файла {name} нет text/base64")
        self.validate()

    def validate(self) -> None:
        if "/" not in self.directories:
            raise ValueError("VFS: отсутствует корневой каталог /")
        overlap = self.directories.intersection(self.files)
        if overlap:
            raise ValueError(f"VFS: путь занят и файлом, и каталогом: {sorted(overlap)[0]}")
        for path in (*self.directories, *self.files):
            normalized = posixpath.normpath(path)
            if not path.startswith("/") or path != normalized or path.startswith("//"):
                raise ValueError(f"VFS: неверный абсолютный путь {path}")
            parent = posixpath.dirname(path)
            if path != "/" and parent not in self.directories:
                raise ValueError(f"VFS: нет родителя для {path}")

    def show_motd(self) -> None:
        if "/motd" in self.files:
            text = self.files["/motd"].decode("utf-8", errors="replace")
            print(text, end="" if text.endswith("\\n") else "\\n")

    def resolve(self, path: str, cwd: str) -> str:
        """Разрешить путь, не выходя за пределы виртуального корня."""
        if not path:
            raise ValueError("путь не может быть пустым")
        current = "/" if path.startswith("/") else cwd
        for part in path.split("/"):
            self.require_directory(current)
            if part in ("", "."):
                continue
            if part == "..":
                current = posixpath.dirname(current) or "/"
            else:
                current = posixpath.join(current, part)
                if current not in self.directories and current not in self.files:
                    raise FileNotFoundError(f"путь не найден: {current}")
        if path.endswith("/"):
            self.require_directory(current)
        return current

    def require_directory(self, path: str) -> None:
        if path not in self.directories:
            raise NotADirectoryError(f"не каталог: {path}")

    def list_names(self, path: str, show_all: bool = False) -> list[str]:
        if path in self.files:
            return [posixpath.basename(path)]
        self.require_directory(path)
        result = [".", ".."] if show_all else []
        for item in (*self.directories, *self.files):
            if item == "/" or posixpath.dirname(item) != path:
                continue
            name = posixpath.basename(item)
            if show_all or not name.startswith("."):
                result.append(name)
        return sorted(result)

    def remove(self, path: str, recursive: bool, cwd: str) -> None:
        if path in self.files:
            del self.files[path]
            return
        self.require_directory(path)
        if not recursive:
            raise IsADirectoryError(f"это каталог, нужен -r: {path}")
        if path == "/":
            raise ValueError("rm: нельзя удалять корень VFS")
        if cwd == path or cwd.startswith(path + "/"):
            raise ValueError("rm: нельзя удалять текущий каталог или его родителя")
        prefix = path + "/"
        self.files = {name: data for name, data in self.files.items()
                      if not name.startswith(prefix)}
        self.directories = {name for name in self.directories
                            if name != path and not name.startswith(prefix)}
