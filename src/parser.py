"""Парсер командной строки с раскрытием переменных окружения."""
import os
import re
import shlex


class ParseError(Exception):
    """Ошибка разбора команды."""


_VAR_PATTERN = re.compile(r"\$(?:\{(\w+)\}|(\w+))")


def expand_env_vars(text: str) -> str:
    """Раскрывает $VAR и ${VAR} из окружения реальной ОС."""
    def replacer(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        return os.environ.get(name, "")

    return _VAR_PATTERN.sub(replacer, text)


def parse(line: str) -> tuple[str, list[str]]:
    """Разбирает строку на команду и аргументы.

    Поддерживает кавычки и раскрытие переменных окружения.
    """
    expanded = expand_env_vars(line.strip())
    if not expanded:
        raise ParseError("Пустая команда")

    try:
        parts = shlex.split(expanded)
    except ValueError as exc:
        raise ParseError(f"Ошибка разбора: {exc}") from exc

    if not parts:
        raise ParseError("Пустая команда")

    return parts[0], parts[1:]