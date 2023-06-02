from __future__ import annotations

import ctypes
import re
import signal
import sys

libc = ctypes.CDLL("libc.so.6")

PASSWORD_WORDS = [
    "كلمه السر",  # Arabic
    "密码",  # Chinese Simplified
    "密碼",  # Chinese Traditional
    "password",  # English
    "mot de passe",  # French
    "passwort",  # German
    "parola d'ordine",  # Italian
    "비밀번호",  # Korean
    "parole",  # Latvian, Lithuanian
    "senha",  # Portuguese
    "пароль",  # Russian
    "contraseña",  # Spanish
]
PASSWORD_REGEXES = [re.compile(fr".*{p}:(.+)", re.I) for p in PASSWORD_WORDS]

PASSWORD_STRIP = [
    '"',
    "'",
    "입니다",
    "이에요",
]


def set_death_signal(sig=signal.SIGTERM):
    if 'linux' not in sys.platform:
        return None

    def process_control():
        return libc.prctl(1, sig)
    return process_control


class TimeoutException(Exception):
    pass


class alarm_clock:
    """A context manager that causes an exception to be raised after a timeout."""

    def __init__(self, timeout):
        self.timeout = timeout
        self.alarm_default = signal.getsignal(signal.SIGALRM)

    def __enter__(self):
        # noinspection PyUnusedLocal
        def handler(signum, frame):
            raise TimeoutException("Timeout")

        signal.signal(signal.SIGALRM, handler)

        signal.alarm(self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.alarm_default)


def extract_passwords(text: str) -> set[str]:
    passwords: set[str] = set()
    text_split, text_split_n = set(text.split()), set(text.split("\n"))
    passwords.update(text_split)
    passwords.update(re.split(r"\W+", text))
    for i, r in enumerate(PASSWORD_REGEXES):
        for line in text_split:
            if PASSWORD_WORDS[i] in line.lower():
                passwords.update(re.split(r, line))
        for line in text_split_n:
            if PASSWORD_WORDS[i] in line.lower():
                passwords.update(re.split(r, line))
    for p in list(passwords):
        p = p.strip()
        # We can assume that at least one of the strip_char won't be there, to have the simple space stripping option
        passwords.update([p.strip(strip_char) for strip_char in PASSWORD_STRIP])
    return passwords
