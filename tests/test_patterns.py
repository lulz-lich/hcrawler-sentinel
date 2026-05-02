from hcrawler.patterns import (
    extract_emails,
    extract_ipv4s,
    extract_phones,
    extract_secret_hints,
    is_valid_cnpj,
    is_valid_cpf,
)


def test_extract_emails():
    assert extract_emails("Contact admin@example.com") == {"admin@example.com"}


def test_extract_phones():
    assert "+55 11 99999-9999" in extract_phones("Phone +55 11 99999-9999")


def test_valid_cpf():
    assert is_valid_cpf("529.982.247-25")


def test_invalid_cpf():
    assert not is_valid_cpf("111.111.111-11")


def test_valid_cnpj():
    assert is_valid_cnpj("11.222.333/0001-81")


def test_secret_hints():
    hints = extract_secret_hints("api_key token password")
    assert "api_key" in hints
    assert "token" in hints
    assert "password" in hints


def test_ipv4s():
    found = extract_ipv4s("192.168.0.1 999.1.1.1")
    assert "192.168.0.1" in found
    assert "999.1.1.1" not in found
