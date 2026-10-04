"""Виртуальная файловая система (in-memory), загружаемая из ZIP-архива."""
from __future__ import annotations

import base64
import zipfile
from dataclasses import dataclass, field


@dataclass
class VFSNode:
    """Узел VFS — файл или директория."""

    name: str
    is_dir: bool
    content: str = ""
    children: dict[str, "VFSNode"] = field(default_factory=dict)


class VFS:
    """Виртуальная ФС. Загружается из ZIP, хранится в памяти."""

    def __init__(self, name: str = "vfs"):
        self.name = name
        self.root = VFSNode("/", is_dir=True)
        self.cwd = self.root

    def load_from_zip(self, path: str) -> None:
        """Загружает VFS из ZIP-архива. Бинарные файлы — в base64."""
        try:
            with zipfile.ZipFile(path, "r") as zf:
                self.root = VFSNode("/", is_dir=True)
                self.cwd = self.root
                self._build_from_zip(zf)
        except FileNotFoundError as exc:
            raise RuntimeError(f"VFS не найден: {path}") from exc
        except zipfile.BadZipFile as exc:
            raise RuntimeError(f"Неверный формат VFS: {path}") from exc

    def _build_from_zip(self, zf: zipfile.ZipFile) -> None:
        """Строит дерево узлов из содержимого ZIP."""
        for info in zf.infolist():
            parts = [p for p in info.filename.split("/") if p]
            if not parts:
                continue

            node = self.root
            for part in parts[:-1]:
                if part not in node.children:
                    node.children[part] = VFSNode(part, is_dir=True)
                node = node.children[part]

            last = parts[-1]
            if info.is_dir():
                if last not in node.children:
                    node.children[last] = VFSNode(last, is_dir=True)
            else:
                raw = zf.read(info.filename)
                try:
                    content = raw.decode("utf-8")
                except UnicodeDecodeError:
                    content = base64.b64encode(raw).decode("ascii")
                node.children[last] = VFSNode(last, is_dir=False, content=content)

    def save_to_zip(self, path: str) -> None:
        """Сохраняет VFS обратно в ZIP-архив."""
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            self._write_node(self.root, "", zf)

    def _write_node(self, node: VFSNode, prefix: str, zf: zipfile.ZipFile) -> None:
        for name, child in node.children.items():
            full = f"{prefix}{name}"
            if child.is_dir:
                zf.writestr(full + "/", b"")
                self._write_node(child, full + "/", zf)
            else:
                try:
                    data = base64.b64decode(child.content, validate=True)
                except Exception:
                    data = child.content.encode("utf-8")
                zf.writestr(full, data)

    def resolve(self, path: str) -> VFSNode:
        """Возвращает узел по пути."""
        if not path or path == "/":
            return self.root

        if path.startswith("/"):
            node = self.root
            parts = [p for p in path.split("/") if p]
        else:
            node = self.cwd
            parts = [p for p in path.split("/") if p]

        for part in parts:
            if part == ".":
                continue
            if part == "..":
                parent = self._find_parent(node)
                node = parent if parent else self.root
                continue
            if not node.is_dir or part not in node.children:
                raise FileNotFoundError(f"Нет такого пути: {path}")
            node = node.children[part]
        return node

    def _find_parent(self, target: VFSNode) -> VFSNode | None:
        """Ищет родителя узла."""
        def walk(node: VFSNode) -> VFSNode | None:
            for child in node.children.values():
                if child is target:
                    return node
                if child.is_dir:
                    found = walk(child)
                    if found:
                        return found
            return None
        return walk(self.root)