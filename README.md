# Эмулятор командной оболочки ОС

**Дисциплина:** Конфигурационное управление
**Институт:** Информационных технологий
**Кафедра:** Корпоративных информационных систем
**Преподаватель:** П.Н. Советов
**Семестр:** 3 семестр (осенний) 2026/2027 учебного года
**Группа:** УНБО-06-25
**Автор:** Нижнецов Дмитрий
**Вариант:** 20

## Описание

GUI-эмулятор UNIX-подобной командной строки с виртуальной файловой системой (VFS), загружаемой из ZIP-архива. Все операции выполняются в памяти.

## Структура проекта

    src/
      main.py       # GUI + точка входа + запуск скриптов
      parser.py     # парсер с раскрытием переменных окружения
      vfs.py        # виртуальная файловая система (ZIP)
      commands.py   # команды: ls, cd, tac, du, mv, vfs-save
    vfs/
      minimal.zip       # только motd
      few_files.zip     # несколько файлов + папка docs
      deep.zip          # иерархия 3+ уровня
    scripts/        # тестовые стартовые скрипты
    os_scripts/     # обёртки для запуска на разных ОС
    docs/           # скриншоты
    tests/          # тесты

## Установка

    git clone https://github.com/Dmitry-Nizhnetsov/kishlak.git
    cd kishlak
    pip install -r requirements.txt

## Запуск

    # GUI без VFS
    python3 -m src.main

    # GUI с VFS
    python3 -m src.main --vfs vfs/deep.zip

    # со стартовым скриптом
    python3 -m src.main --vfs vfs/deep.zip --script scripts/test_stage3.txt

    # через скрипт ОС
    ./os_scripts/run_deep.sh

## Этап 1. REPL

- **GUI** на tkinter.
- Заголовок окна: `Эмулятор - [username@hostname]` — на основе реальных данных ОС.
- **Парсер** с раскрытием `$HOME`, `${USER}`.
- Команды-заглушки `ls`, `cd`.
- Команда `exit`.
- Обработка ошибок неизвестных команд.

### Демонстрация

![Скриншот GUI](docs/screenshot.png)

    vfs:/$ ls -la
    ls: ['-la'] (заглушка)
    vfs:/$ cd $HOME
    cd: ['/Users/dmitrijniznecov'] (заглушка)
    vfs:/$ foo
    Ошибка: неизвестная команда 'foo'

## Этап 2. Конфигурация

- Параметры командной строки: `--vfs`, `--script`.
- **Стартовый скрипт пропускает ошибочные строки** и имитирует диалог.
- Отладочный вывод всех параметров при запуске.
- Скрипты реальной ОС в `os_scripts/`.

### Демонстрация

    $ python3 -m src.main --script scripts/test_stage2.txt
    ========================================
    Параметры запуска:
      VFS: None
      Скрипт: scripts/test_stage2.txt
    ========================================
    >>> ls
    ls: [] (заглушка)
    >>> unknown_command
    Ошибка: неизвестная команда 'unknown_command'
    >>> cd $HOME
    cd: ['/Users/dmitrijniznecov'] (заглушка)

## Этап 3. VFS из ZIP

- Все операции **в памяти**, VFS не модифицируется на диске.
- Источник — **ZIP-архив**. Бинарные данные — base64.
- Обработка ошибок загрузки (файл не найден, неверный формат).
- Команда **`vfs-save путь`** — сохранение VFS обратно в ZIP.
- Реализованные команды: `ls`, `cd`, `tac`, `du`, `mv`, `vfs-save`.
- Три тестовых VFS: минимальный, несколько файлов, глубокая иерархия (≥3 уровней).

### Демонстрация

    $ python3 -m src.main --vfs vfs/deep.zip --script scripts/test_stage3.txt
    ========================================
    Параметры запуска:
      VFS: vfs/deep.zip
      Скрипт: scripts/test_stage3.txt
    ========================================
    >>> ls
    a
    motd
    multiline.txt
    >>> cd a/b/c
    >>> ls
    deep.txt
    >>> tac deep.txt
    deep file
    >>> du /
    38	/
    >>> cd /
    >>> tac multiline.txt
    line3
    line2
    line1
    >>> vfs-save /tmp/vfs_saved.zip
    VFS сохранена в /tmp/vfs_saved.zip
    >>> exit

## Команды

| Команда | Описание |
|---------|----------|
| `ls [путь]` | Список файлов в директории |
| `cd [путь]` | Смена текущей директории |
| `tac файл` | Вывод файла в обратном порядке строк |
| `du [путь]` | Размер файла или директории в байтах |
| `mv источник назначение` | Перемещение/переименование |
| `vfs-save путь` | Сохранить VFS в ZIP-архив |
| `exit` | Выход из эмулятора |

## Скрипты ОС

- `os_scripts/run_stage1.sh` — GUI без VFS
- `os_scripts/run_stage2.sh` — со стартовым скриптом
- `os_scripts/run_deep.sh` — с глубокой VFS и скриптом

## Тесты

    pytest tests/ -v
## Этап 3. VFS из ZIP

- Все операции **в памяти**, VFS не модифицируется на диске.
- Источник — **ZIP-архив**. Бинарные данные — base64.
- Обработка ошибок загрузки (файл не найден, неверный формат).
- Команда **`vfs-save путь`** — сохранение VFS обратно в ZIP.
- Реализованные команды: `ls`, `cd`, `tac`, `du`, `mv`, `vfs-save`.
- Три тестовых VFS: минимальный, несколько файлов, глубокая иерархия (≥3 уровней).

### Демонстрация

    $ python3 -m src.main --vfs vfs/deep.zip --script scripts/test_stage3.txt
    ========================================
    Параметры запуска:
      VFS: vfs/deep.zip
      Скрипт: scripts/test_stage3.txt
    ========================================
    >>> ls
    a
    motd
    multiline.txt
    >>> cd a/b/c
    >>> ls
    deep.txt
    >>> tac deep.txt
    deep file
    >>> du /
    38	/
    >>> cd /
    >>> tac multiline.txt
    line3
    line2
    line1
    >>> vfs-save /tmp/vfs_saved.zip
    VFS сохранена в /tmp/vfs_saved.zip
    >>> exit