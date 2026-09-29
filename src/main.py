"""Точка входа: GUI-эмулятор оболочки ОС."""
from __future__ import annotations

import argparse
import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from .parser import ParseError, parse


class ShellEmulator:
    """GUI-эмулятор командной оболочки (Этап 1)."""

    def __init__(self, root: tk.Tk, vfs_name: str = "vfs"):
        self.root = root
        self.vfs_name = vfs_name
        self.cwd = "/"

        # Заголовок окна на основе реальных данных ОС
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        self.root.geometry("800x600")

        # Область вывода
        self.output = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 11)
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Метка приглашения
        self.prompt_label = tk.Label(root, text=self._prompt(), anchor="w")
        self.prompt_label.pack(fill=tk.X, padx=5)

        # Поле ввода
        self.entry = tk.Entry(root, font=("Consolas", 11))
        self.entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

        self._print(f"Добро пожаловать в {self.vfs_name}!")
        self._print("Введите 'exit' для выхода.\n")

    def _prompt(self) -> str:
        return f"{self.vfs_name}:{self.cwd}$ "

    def _print(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _on_enter(self, event) -> None:
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if not line.strip():
            return
        self._print(f"{self._prompt()}{line}")
        self._execute(line)
        self.prompt_label.config(text=self._prompt())

    def _execute(self, line: str) -> None:
        try:
            cmd, args = parse(line)
        except ParseError as exc:
            self._print(f"Ошибка: {exc}")
            return

        if cmd == "exit":
            self.root.destroy()
            return

        if cmd == "ls":
            self._print(f"ls: {args} (заглушка)")
            return

        if cmd == "cd":
            self._print(f"cd: {args} (заглушка)")
            return

        self._print(f"Ошибка: неизвестная команда '{cmd}'")


def parse_args() -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", type=str, help="Путь к VFS")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту")
    return parser.parse_args()


def run_script(path: str) -> None:
    """Выполняет стартовый скрипт, пропуская ошибочные строки."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip() or line.strip().startswith("#"):
                    continue

                # Имитация диалога: показываем ввод
                print(f">>> {line}")

                try:
                    cmd, args = parse(line)
                except ParseError as exc:
                    print(f"Ошибка: {exc}")
                    continue

                if cmd == "exit":
                    return
                if cmd == "ls":
                    print(f"ls: {args} (заглушка)")
                elif cmd == "cd":
                    print(f"cd: {args} (заглушка)")
                else:
                    print(f"Ошибка: неизвестная команда '{cmd}'")
    except FileNotFoundError:
        print(f"Ошибка: скрипт '{path}' не найден")


def main() -> None:
    """Точка входа."""
    args = parse_args()

    print("=" * 40)
    print("Параметры запуска:")
    print(f"  VFS: {args.vfs}")
    print(f"  Скрипт: {args.script}")
    print("=" * 40)

    # Если задан скрипт — выполняем его и выходим
    if args.script:
        run_script(args.script)
        return

    # Иначе — GUI
    root = tk.Tk()
    ShellEmulator(root, vfs_name="vfs")
    root.mainloop()


if __name__ == "__main__":
    main()