import pytest

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_can_be_verified():
    password = "secure-password"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_password_hash_uses_a_new_salt_each_time():
    password = "secure-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True


def test_access_token_round_trip():
    token = create_access_token("admin")

    assert decode_access_token(token) == "admin"


def test_access_token_rejects_modified_token():
    token = create_access_token("admin")

    with pytest.raises(ValueError, match="Недействительный токен"):
        decode_access_token(token + "modified")


def test_access_token_requires_subject():
    from jose import jwt
    from config import settings

    token = jwt.encode(
        {"exp": 9_999_999_999},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Токен не содержит субъект"):
        decode_access_token(token)
