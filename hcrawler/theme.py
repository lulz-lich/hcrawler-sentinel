"""Hacker-style terminal aesthetics and lightweight animation helpers."""

from __future__ import annotations

import random
import sys
import time
from typing import Iterable

from colorama import Fore, Style

NEON_GREEN = Fore.LIGHTGREEN_EX
NEON_CYAN = Fore.CYAN
NEON_RED = Fore.LIGHTRED_EX
NEON_YELLOW = Fore.YELLOW
NEON_MAGENTA = Fore.LIGHTMAGENTA_EX
MUTED = Fore.GREEN
RESET = Style.RESET_ALL

MAIN_BANNERS = [
    r'''
 __    __   ______   _______   ______   __       __  ________  _______
/  |  /  | /      \ /       \ /      \ /  |  _  /  |/        |/       \
$$ |  $$ |/$$$$$$  |$$$$$$$  |$$$$$$  |$$ | / \ $$ |$$$$$$$$/ $$$$$$$  |
$$ |__$$ |$$ |  $$/ $$ |__$$ | /    $$ |$$ |/$  \$$ |$$ |__    $$ |__$$ |
$$    $$ |$$ |      $$    $$< /$$$$$$$ |$$ /$$$  $$ |$$    |   $$    $$<
$$$$$$$$ |$$ |   __ $$$$$$$  |$$    $$ |$$ $$/$$ $$ |$$$$$/    $$$$$$$  |
$$ |  $$ |$$ \__/  |$$ |  $$ |$$$$$$$$/ $$$$/  $$$$ |$$ |_____ $$ |  $$ |
$$ |  $$ |$$    $$/ $$ |  $$ |$$       |$$$/    $$$ |$$       |$$ |  $$ |
$$/   $$/  $$$$$$/  $$/   $$/  $$$$$$$/ $$/      $$/ $$$$$$$$/ $$/   $$/
''',
    r'''
██╗  ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗
██║  ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗
███████║██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝
██╔══██║██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗
██║  ██║╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝
''',
    r'''
┌─────────────────────────────────────────────────────────────────────┐
│  _   _  _____                         _             ____            │
│ | | | |/ ____|                       | |           / __ \           │
│ | |_| | |      _ __ __ ___      _____| | ___ _ __ | |  | |_ __     │
│ |  _  | |     | '__/ _` \ \ /\ / / _ \ |/ _ \ '__|| |  | | '_ \    │
│ | | | | |____ | | | (_| |\ V  V /  __/ |  __/ |   | |__| | |_) |   │
│ |_| |_|\_____||_|  \__,_| \_/\_/ \___|_|\___|_|    \____/| .__/    │
│                                                          | |        │
│                                                          |_|        │
└─────────────────────────────────────────────────────────────────────┘
''',
    r'''
 ▄█    █▄     ▄████████    ▄████████    ▄█     █▄   ▄█        ▄████████    ▄████████
███    ███   ███    ███   ███    ███   ███     ███ ███       ███    ███   ███    ███
███    ███   ███    █▀    ███    ███   ███     ███ ███       ███    █▀    ███    ███
███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀   ███     ███ ███      ▄███▄▄▄      ▄███▄▄▄▄██▀
███    ███ ▀▀███▀▀▀     ▀▀███▀▀▀▀▀     ███     ███ ███     ▀▀███▀▀▀     ▀▀███▀▀▀▀▀
███    ███   ███    █▄  ▀███████████   ███     ███ ███       ███    █▄  ▀███████████
███    ███   ███    ███   ███    ███   ███ ▄█▄ ███ ███▌    ▄ ███    ███   ███    ███
 ▀██████▀    ██████████   ███    ███    ▀███▀███▀  █████▄▄██ ██████████   ███    ███
                         ███    ███                         ▀                ███    ███
''',
    r'''
 .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. |
| |  ____  ____  | || |     ______   | || |  _______     | || |      __      | |
| | |_  _||_  _| | || |   .' ___  |  | || | |_   __ \    | || |     /  \     | |
| |   \ \  / /   | || |  / .'   \_|  | || |   | |__) |   | || |    / /\ \    | |
| |    > `' <    | || |  | |         | || |   |  __ /    | || |   / ____ \   | |
| |  _/ /'`\ \_  | || |  \ `.___.'\  | || |  _| |  \ \_  | || | _/ /    \ \_ | |
| | |____||____| | || |   `._____.'  | || | |____| |___| | || ||____|  |____|| |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'
''',
]

COMMAND_ART = {
    'crawl': r'''
   ________  ________  ________  ___       __
  / ____/ / / / __/ / / / __/ / / / |     / /
 / /   / /_/ / /_/ /_/ / /_/ /_/ /| | /| / /
/ /___/ __  / __/ __  / __/ __  / | |/ |/ /
\____/_/ /_/_/ /_/ /_/_/ /_/ /_/  |__/|__/
''',
    'diff': r'''
    ____  _________  ______
   / __ \/  _/ __/ |/ / __/
  / / / // // _//    / _/
 / /_/ // // /_/ /|  / /
/_____/___/_/_/_/ |_/_/
''',
    'doctor': r'''
    ____  ____  ________  _________  __
   / __ \/ __ \/ ____/ / / /_  __/ |/ /
  / / / / / / / /   / / / / / /  |   /
 / /_/ / /_/ / /___/ /_/ / / /  /   |
/_____/_____/\____/\____/ /_/  /_/|_|
''',
}

SKULL_ART = [
    r'''
             _,met$$$$$gg.
          ,g$$$$$$$$$$$$$$$P.
        ,g$$P""       """Y$$.".
       ,$$P'              `$$$.
     ',$$P       ,ggs.     `$$b:
     `d$$'     ,$P"'   .    $$$
      $$P      d$'     ,    $$P
      $$:      $$.   -    ,d$$'
      $$;      Y$b._   _,d$P'
      Y$$.    `.`"Y$$$$P"'
      `$$b      "-.__
       `Y$$
        `Y$$.
          `$$b.
            `Y$$b.
               `"Y$b._
                   `""""
''',
    r'''
  _________ _______  _______  ___  __    _
 |\__   __/(  ____ \(  ___  )(  )(  \  ( |
    ) (   | (    \/| (   ) || ||   \ | |
    | |   | (__    | (___) || || (\ \) |
    | |   |  __)   |  ___  || || | \   |
    | |   | (      | (   ) || || )  \  |
    | |   | (____/\| )   ( || ||/    )_|
    )_(   (_______/|/     \|( )|\____) )
                               |/  \___/
''',
    r'''
      .--.
     |o_o |
     |:_/ |
    //   \ \
   (|     | )
  /'\_   _/`\\
  \___)=(___/
''',
]

BOOT_LINES = [
    'binding terminal glyph matrix',
    'warming reconnaissance pipeline',
    'arming fingerprint engine',
    'synchronizing crawler nodes',
    'loading ASCII overlays',
    'calibrating stealth-by-consent profile',
    'mounting neon dashboard',
    'injecting terminal theatrics',
]

QUOTES = [
    'we scan because curiosity is undefeated',
    'signal over noise // scope over chaos',
    'authorized reconnaissance only',
    'green text, dark screen, clean reports',
]


def _out(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


def typewrite(text: str, *, delay: float = 0.003, enabled: bool = True, newline: bool = True, color: str = '') -> None:
    if not enabled:
        _out(color + text + RESET + ('\n' if newline else ''))
        return
    _out(color)
    for char in text:
        _out(char)
        time.sleep(delay)
    if color:
        _out(RESET)
    if newline:
        _out('\n')


def splash(*, enabled: bool = True, command: str | None = None) -> None:
    banner = random.choice(MAIN_BANNERS)
    color = random.choice([NEON_GREEN, NEON_CYAN, NEON_MAGENTA])
    if enabled:
        for line in banner.splitlines():
            if line.strip():
                typewrite(line, delay=0.0008, enabled=True, color=color)
            else:
                print()
    else:
        print(color + banner + RESET)
    if command and command in COMMAND_ART:
        print(NEON_CYAN + COMMAND_ART[command] + RESET)
    print(NEON_GREEN + '[ HCrawler Sentinel // terminal assault aesthetics online ]' + RESET)
    print(MUTED + f'[ {random.choice(QUOTES)} ]' + RESET)
    print()


def boot_sequence(*, enabled: bool = True) -> None:
    for idx, line in enumerate(BOOT_LINES, start=1):
        prefix = f'[{idx:02d}/{len(BOOT_LINES):02d}] '
        typewrite(prefix + line + ' ... ok', delay=0.0018, enabled=enabled, color=MUTED)
    print()


def rule(label: str = '') -> None:
    bar = '═' * 74
    if label:
        print(NEON_CYAN + f'╔{bar}╗' + RESET)
        centered = f' {label} '.center(74, '═')
        print(NEON_CYAN + f'║{centered}║' + RESET)
        print(NEON_CYAN + f'╚{bar}╝' + RESET)
    else:
        print(NEON_CYAN + '═' * 76 + RESET)


def print_kv_block(title: str, rows: Iterable[tuple[str, object]]) -> None:
    width = 86
    print(NEON_CYAN + '┌' + '─' * (width - 2) + '┐' + RESET)
    heading = f' {title} '.center(width - 2, '─')
    print(NEON_CYAN + '│' + RESET + NEON_GREEN + heading + RESET + NEON_CYAN + '│' + RESET)
    print(NEON_CYAN + '├' + '─' * (width - 2) + '┤' + RESET)
    for key, value in rows:
        key_text = f' {key:<22}'
        value_text = f' {value}'
        content = (key_text + '│' + value_text)[: width - 2]
        print(NEON_CYAN + '│' + RESET + content.ljust(width - 2) + NEON_CYAN + '│' + RESET)
    print(NEON_CYAN + '└' + '─' * (width - 2) + '┘' + RESET)


def phase(label: str, *, enabled: bool = True, loops: int = 18) -> None:
    frames = ['[    ]', '[=   ]', '[==  ]', '[=== ]', '[ ===]', '[  ==]', '[   =]', '[====]']
    if not enabled:
        print(MUTED + f'{label} ... done' + RESET)
        return
    for idx in range(loops):
        _out('\r' + NEON_GREEN + frames[idx % len(frames)] + RESET + f' {label}')
        time.sleep(0.035)
    _out('\r' + NEON_GREEN + '[done]' + RESET + f' {label}' + ' ' * 8 + '\n')


def event(message: str, level: str = 'info') -> None:
    color = {
        'info': NEON_GREEN,
        'warn': NEON_YELLOW,
        'error': NEON_RED,
        'accent': NEON_MAGENTA,
    }.get(level, NEON_GREEN)
    icon = {
        'info': '[+]',
        'warn': '[!]',
        'error': '[x]',
        'accent': '[*]',
    }.get(level, '[+]')
    print(color + f'{icon} {message}' + RESET)


def mini_matrix(*, enabled: bool = True, rows: int = 8, width: int = 86) -> None:
    if not enabled:
        return
    alphabet = '01ABCDEF$#@%*+-[]{}<>/\\'
    for _ in range(rows):
        line = ''.join(random.choice(alphabet) for _ in range(width))
        print(MUTED + line + RESET)
        time.sleep(0.008)
    print()


def random_art(*, enabled: bool = True) -> None:
    if not enabled:
        return
    art = random.choice(SKULL_ART)
    color = random.choice([NEON_RED, NEON_MAGENTA, NEON_CYAN])
    print(color + art + RESET)
    print()
