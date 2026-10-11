"""Разбор командной строки эмулятора."""

import shlex


def parse_command(line: str) -> list[str]:
    """Разобрать строку с поддержкой кавычек и комментариев."""
    try:
        return shlex.split(line, comments=True, posix=True)
    except ValueError as error:
        raise ValueError("незакрытая кавычка или некорректное экранирование") from error


def parse_options(args: list[str], allowed: str) -> tuple[set[str], list[str]]:
    """Вернуть множество коротких флагов и позиционные аргументы."""
    flags: set[str] = set()
    paths: list[str] = []
    options = True
    for arg in args:
        if options and arg == "--":
            options = False
        elif options and arg.startswith("-") and arg != "-":
            for flag in arg[1:]:
                if flag not in allowed:
                    raise ValueError(f"неизвестный флаг: -{flag}")
                flags.add(flag)
        else:
            paths.append(arg)
    return flags, paths


def one_path(args: list[str], default: str) -> str:
    if len(args) > 1:
        raise ValueError("нужен не более одного пути")
    return args[0] if args else default


def require_no_args(args: list[str], command: str) -> None:
    if args:
        raise ValueError(f"{command}: аргументы не нужны")
