"""Точка входа: GUI-эмулятор оболочки ОС."""
from __future__ import annotations

import argparse
import getpass
import socket
import sys
import tkinter as tk
from tkinter import scrolledtext

from . import commands
from .parser import ParseError, parse
from .vfs import VFS


class ShellEmulator:
    """GUI-эмулятор командной оболочки."""

    def __init__(self, root: tk.Tk, vfs: VFS):
        self.root = root
        self.vfs = vfs

        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        self.root.geometry("800x600")

        self.output = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 11)
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.prompt_label = tk.Label(root, text=self._prompt(), anchor="w")
        self.prompt_label.pack(fill=tk.X, padx=5)

        self.entry = tk.Entry(root, font=("Consolas", 11))
        self.entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

        self._print(f"Добро пожаловать в {self.vfs.name}!")
        self._print("Введите 'exit' для выхода.\n")
        self._show_motd()

    def _prompt(self) -> str:
        return f"{self.vfs.name}:{self.vfs.cwd.name}$ "

    def _print(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _show_motd(self) -> None:
        motd = self.vfs.root.children.get("motd")
        if motd and not motd.is_dir:
            self._print(motd.content)

    def _on_enter(self, event) -> None:
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if not line.strip():
            return
        self._print(f"{self._prompt()}{line}")
        self._execute(line)
        try:
            self.prompt_label.config(text=self._prompt())
        except tk.TclError:
            pass

    def _execute(self, line: str) -> None:
        try:
            cmd, args = parse(line)
        except ParseError as exc:
            self._print(f"Ошибка: {exc}")
            return

        handler = get_handler(cmd)
        if handler is None:
            self._print(f"Ошибка: неизвестная команда '{cmd}'")
            return

        try:
            result = handler(self.vfs, args)
            if result:
                self._print(result)
        except commands.CommandError as exc:
            self._print(f"Ошибка: {exc}")
        except FileNotFoundError as exc:
            self._print(f"Ошибка: {exc}")
        except SystemExit:
            self.root.destroy()


HANDLERS = {
    "ls": commands.cmd_ls,
    "cd": commands.cmd_cd,
    "tac": commands.cmd_tac,
    "du": commands.cmd_du,
    "mv": commands.cmd_mv,
    "vfs-save": commands.cmd_vfs_save,
    "exit": commands.cmd_exit,
}


def get_handler(cmd: str):
    return HANDLERS.get(cmd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", type=str, help="Путь к ZIP-архиву VFS")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту")
    return parser.parse_args()


def run_script(vfs: VFS, path: str) -> None:
    """Выполняет стартовый скрипт, пропуская ошибочные строки."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip() or line.strip().startswith("#"):
                    continue
                print(f">>> {line}")
                try:
                    cmd, args = parse(line)
                except ParseError as exc:
                    print(f"Ошибка: {exc}")
                    continue
                handler = get_handler(cmd)
                if handler is None:
                    print(f"Ошибка: неизвестная команда '{cmd}'")
                    continue
                try:
                    result = handler(vfs, args)
                    if result:
                        print(result)
                except Exception as exc:  # noqa: BLE001
                    print(f"Ошибка: {exc}")
    except FileNotFoundError:
        print(f"Ошибка: скрипт '{path}' не найден")


def main() -> None:
    args = parse_args()

    print("=" * 40)
    print("Параметры запуска:")
    print(f"  VFS: {args.vfs}")
    print(f"  Скрипт: {args.script}")
    print("=" * 40)

    vfs = VFS(name="vfs")
    if args.vfs:
        try:
            vfs.load_from_zip(args.vfs)
        except RuntimeError as exc:
            print(f"Ошибка загрузки VFS: {exc}")
            sys.exit(1)

    if args.script:
        run_script(vfs, args.script)
        return

    root = tk.Tk()
    ShellEmulator(root, vfs)
    root.mainloop()


if __name__ == "__main__":
    main()