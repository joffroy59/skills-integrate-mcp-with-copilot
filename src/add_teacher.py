"""Provision a teacher account in teachers.json."""

import getpass
import json
import sys

from teacher_auth import TEACHERS_FILE, load_teachers, make_password_record


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        raise SystemExit("Usage: python add_teacher.py <username>")

    username = sys.argv[1].strip()
    if ":" in username:
        raise SystemExit("Username must not contain a colon")

    teachers = load_teachers(TEACHERS_FILE)
    if username in teachers:
        raise SystemExit(f"Teacher {username!r} already exists")

    password = getpass.getpass("Teacher password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password:
        raise SystemExit("Password must not be empty")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    teachers[username] = make_password_record(password)
    TEACHERS_FILE.write_text(
        json.dumps({"teachers": teachers}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added teacher {username!r}. Restart the application to load the account.")


if __name__ == "__main__":
    main()
