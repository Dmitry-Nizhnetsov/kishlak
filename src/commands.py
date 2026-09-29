"""Реализация команд эмулятора."""
from __future__ import annotations

from .vfs import VFS, VFSNode


class CommandError(Exception):
    """Ошибка выполнения команды."""


def cmd_ls(vfs: VFS, args: list[str]) -> str:
    """Вывод содержимого директории."""
    target = args[0] if args else "."
    node = vfs.resolve(target)
    if not node.is_dir:
        return node.name
    names = sorted(node.children.keys())
    return "\n".join(names) if names else ""


def cmd_cd(vfs: VFS, args: list[str]) -> str:
    """Смена текущей директории."""
    target = args[0] if args else "/"
    node = vfs.resolve(target)
    if not node.is_dir:
        raise CommandError(f"cd: {target}: не директория")
    vfs.cwd = node
    return ""


def cmd_tac(vfs: VFS, args: list[str]) -> str:
    """Вывод файла в обратном порядке строк."""
    if not args:
        raise CommandError("tac: не указан файл")
    node = vfs.resolve(args[0])
    if node.is_dir:
        raise CommandError(f"tac: {args[0]}: это директория")
    lines = node.content.splitlines()
    return "\n".join(reversed(lines))


def cmd_du(vfs: VFS, args: list[str]) -> str:
    """Размер файла или директории в байтах."""
    target = args[0] if args else "."
    node = vfs.resolve(target)
    size = _node_size(node)
    return f"{size}\t{target}"


def _node_size(node: VFSNode) -> int:
    if not node.is_dir:
        return len(node.content.encode("utf-8"))
    return sum(_node_size(c) for c in node.children.values())


def cmd_mv(vfs: VFS, args: list[str]) -> str:
    """Перемещение/переименование файла или директории."""
    if len(args) < 2:
        raise CommandError("mv: нужен источник и назначение")
    src_path, dst_path = args[0], args[1]
    src = vfs.resolve(src_path)

    parent = vfs._find_parent(src)
    if parent is None:
        raise CommandError("mv: не удалось найти родителя")
    del parent.children[src.name]

    try:
        dst = vfs.resolve(dst_path)
        if dst.is_dir:
            dst.children[src.name] = src
        else:
            dst_parent = vfs._find_parent(dst)
            if dst_parent is None:
                raise CommandError("mv: неверное назначение")
            del dst_parent.children[dst.name]
            dst_parent.children[src.name] = src
    except FileNotFoundError:
        new_parent_path = "/".join(dst_path.split("/")[:-1]) or "."
        new_name = dst_path.split("/")[-1]
        new_parent = vfs.resolve(new_parent_path)
        if not new_parent.is_dir:
            raise CommandError("mv: назначение не директория")
        src.name = new_name
        new_parent.children[new_name] = src

    return ""


def cmd_vfs_save(vfs: VFS, args: list[str]) -> str:
    """Сохраняет текущее состояние VFS на диск в ZIP."""
    if not args:
        raise CommandError("vfs-save: укажите путь")
    try:
        vfs.save_to_zip(args[0])
    except OSError as exc:
        raise CommandError(f"vfs-save: {exc}") from exc
    return f"VFS сохранена в {args[0]}"


def cmd_exit(vfs: VFS, args: list[str]) -> str:
    """Выход из эмулятора."""
    raise SystemExit(0)