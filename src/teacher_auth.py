"""Teacher credential loading and password verification."""

import hashlib
import hmac
import json
import logging
import secrets
from pathlib import Path
from typing import Any

TEACHERS_FILE = Path(__file__).with_name("teachers.json")
PASSWORD_ITERATIONS = 310_000


def load_teachers(path: Path = TEACHERS_FILE) -> dict[str, dict[str, str]]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logging.warning(
            "No teacher accounts configured; run add_teacher.py to enable enrollment management."
        )
        return {}
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Unable to load teacher credentials from {path}") from error

    if not isinstance(data, dict) or not isinstance(data.get("teachers"), dict):
        raise RuntimeError(f"Invalid teacher credentials format in {path}")

    teachers = data["teachers"]
    for username, record in teachers.items():
        if (
            not isinstance(username, str)
            or not isinstance(record, dict)
            or not isinstance(record.get("salt"), str)
            or not isinstance(record.get("password_hash"), str)
        ):
            raise RuntimeError(f"Invalid credentials for teacher {username!r} in {path}")
        try:
            bytes.fromhex(record["salt"])
            bytes.fromhex(record["password_hash"])
        except ValueError as error:
            raise RuntimeError(f"Invalid password hash for teacher {username!r}") from error
    return teachers


def make_password_record(password: str) -> dict[str, str]:
    if not password:
        raise ValueError("Password must not be empty")

    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return {"salt": salt.hex(), "password_hash": password_hash.hex()}


def verify_teacher(
    username: str,
    password: str,
    teachers: dict[str, dict[str, str]],
) -> bool:
    record = teachers.get(username)
    if record is None:
        return False

    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(record["salt"]),
        PASSWORD_ITERATIONS,
    )
    return hmac.compare_digest(candidate_hash.hex(), record["password_hash"])
