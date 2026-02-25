"""
Кастомный генератор PK.
Без: UUID, random, стандартных функций Postgres, integer auto-increment.
"""

import time
from threading import Lock
from typing import Optional

# Свой алфавит для кодирования (32 символа — компактный вывод)
ALPHABET = "7k9mX2pQ5vR8sT4wY6zB1cD3fG0hJ"

# Префиксы по типу сущности (опционально, для читаемости)
ENTITY_PREFIXES = {
    "task": "t",
    "category": "c",
    "telegram_user": "u",
}

_sequence = 0
_lock = Lock()


def _polynomial_hash(data: str, base: int = 37, mod: int = (1 << 61) - 1) -> int:
    """
    Полиномиальный rolling hash.
    Без hashlib, uuid, random.
    """
    result = 0
    for char in data:
        result = (result * base + ord(char)) % mod
    return result


def _to_custom_base(num: int, alphabet: str = ALPHABET) -> str:
    """Перевод числа в систему счисления с кастомным алфавитом."""
    if num == 0:
        return alphabet[0]
    base_len = len(alphabet)
    digits = []
    while num:
        digits.append(alphabet[num % base_len])
        num //= base_len
    return "".join(reversed(digits))


def _mix_bits(value: int) -> int:
    """
    Дополнительное перемешивание битов (не стандартная функция).
    """
    x = value & 0xFFFFFFFFFFFFFFFF
    x ^= (x >> 16) & 0xFFFFFFFF
    x = (x * 0x85EBCA6B) & 0xFFFFFFFFFFFFFFFF
    x ^= (x >> 13) & 0xFFFFFFFF
    x = (x * 0xC2B2AE35) & 0xFFFFFFFFFFFFFFFF
    x ^= (x >> 16) & 0xFFFFFFFF
    return x & 0xFFFFFFFFFFFFFFFF


def generate_id(entity_type: str, sequence_source: Optional[int] = None) -> str:
    """
    Генерирует уникальный строковый ID.

    Args:
        entity_type: тип сущности ('task', 'category', 'telegram_user')
        sequence_source: внешний счётчик (Redis/БД). Если None — in-memory.

    Returns:
        Строка вида "t_7k9mX2pQ5vR8sT" (префикс + закодированный хеш)
    """
    global _sequence
    with _lock:
        if sequence_source is not None:
            seq = sequence_source
        else:
            _sequence += 1
            seq = _sequence

    timestamp_ns = time.time_ns()
    prefix = ENTITY_PREFIXES.get(entity_type, "x")

    # Уникальная комбинация
    raw = f"{timestamp_ns}:{seq}:{prefix}"
    hash_val = _polynomial_hash(raw)

    # Перемешивание битов
    mixed = _mix_bits(hash_val & 0xFFFFFFFFFFFFFFFF)

    # Кодирование в кастомную систему счисления
    encoded = _to_custom_base(mixed)

    # Фиксированная длина (14 символов)
    return f"{prefix}_{encoded[:14].zfill(14)}"
