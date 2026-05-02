"""Extraction patterns and Brazilian document validators."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+\d{1,3}\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}\b")
CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_HINT_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|authorization|bearer|"
    r"private[_-]?key|access[_-]?key|aws_access_key_id|aws_secret_access_key|"
    r"client_secret|database_url|db_password|jwt|stripe[_-]?key|github[_-]?token|"
    r"slack[_-]?token|ssh[_-]?key)\b"
)


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_cpf(value: str) -> bool:
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = (total * 10) % 11
    d1 = 0 if d1 == 10 else d1

    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = (total * 10) % 11
    d2 = 0 if d2 == 10 else d2

    return cpf[-2:] == f"{d1}{d2}"


def is_valid_cnpj(value: str) -> bool:
    cnpj = only_digits(value)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6] + w1

    total = sum(int(digit) * weight for digit, weight in zip(cnpj[:12], w1))
    d1 = 11 - (total % 11)
    d1 = 0 if d1 >= 10 else d1

    total = sum(int(digit) * weight for digit, weight in zip(cnpj[:13], w2))
    d2 = 11 - (total % 11)
    d2 = 0 if d2 >= 10 else d2

    return cnpj[-2:] == f"{d1}{d2}"


def extract_emails(text: str) -> set[str]:
    return set(EMAIL_RE.findall(text))


def extract_phones(text: str) -> set[str]:
    return set(PHONE_RE.findall(text))


def extract_cpfs(text: str, *, validate: bool = True) -> set[str]:
    found = set(CPF_RE.findall(text))
    return {cpf for cpf in found if is_valid_cpf(cpf)} if validate else found


def extract_cnpjs(text: str, *, validate: bool = True) -> set[str]:
    found = set(CNPJ_RE.findall(text))
    return {cnpj for cnpj in found if is_valid_cnpj(cnpj)} if validate else found


def extract_ipv4s(text: str) -> set[str]:
    values = set(IPV4_RE.findall(text))
    return {value for value in values if all(0 <= int(part) <= 255 for part in value.split("."))}


def extract_secret_hints(text: str) -> set[str]:
    return {match.group(0) for match in SECRET_HINT_RE.finditer(text)}
