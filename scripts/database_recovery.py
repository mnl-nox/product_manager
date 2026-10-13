#!/usr/bin/env python3
"""Create and restore consistent, verified SQLite database snapshots."""

from __future__ import annotations

import argparse
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

REQUIRED_TABLES = {"app_users", "products", "finance_entries"}


def validate_database(path: Path) -> None:
    uri = f"{path.resolve().as_uri()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if result is None or result[0] != "ok":
            raise ValueError(f"Integridade SQLite inválida: {result[0] if result else 'sem resultado'}")
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        missing = REQUIRED_TABLES - tables
        if missing:
            raise ValueError("O arquivo não contém o esquema mínimo do Product Manager.")


def _snapshot(source: Path, destination: Path, *, replace: bool) -> None:
    source = source.expanduser().resolve(strict=True)
    destination = destination.expanduser().resolve()
    if source == destination:
        raise ValueError("Origem e destino devem ser arquivos diferentes.")
    if not destination.parent.is_dir():
        raise ValueError("O diretório de destino deve existir.")
    if replace and not destination.exists():
        raise ValueError("A substituição exige um banco de destino existente.")
    if not replace and destination.exists():
        raise FileExistsError("O destino já existe; escolha outro nome.")
    validate_database(source)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    if hasattr(os, "fchmod"):
        os.fchmod(descriptor, 0o600)
    else:
        os.chmod(temporary_name, 0o600)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        source_uri = f"{source.as_uri()}?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True)) as source_connection:
            with closing(sqlite3.connect(temporary)) as destination_connection:
                source_connection.backup(destination_connection)
                destination_connection.commit()
        validate_database(temporary)
        if replace:
            os.replace(temporary, destination)
        else:
            # Hard-link creation is atomic and refuses to overwrite a raced-in file.
            os.link(temporary, destination)
            temporary.unlink()
        os.chmod(destination, 0o600)
    finally:
        temporary.unlink(missing_ok=True)


def backup_database(source: Path, destination: Path) -> None:
    _snapshot(source, destination, replace=False)


def restore_database(backup: Path, destination: Path, *, replace: bool = False) -> None:
    _snapshot(backup, destination, replace=replace)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    backup = commands.add_parser("backup", help="Create a consistent SQLite backup")
    backup.add_argument("source", type=Path)
    backup.add_argument("destination", type=Path)
    restore = commands.add_parser("restore", help="Restore a verified SQLite backup")
    restore.add_argument("backup", type=Path)
    restore.add_argument("destination", type=Path)
    restore.add_argument(
        "--replace", action="store_true",
        help="Replace an existing destination (stop the application first)",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "backup":
            backup_database(args.source, args.destination)
        else:
            restore_database(args.backup, args.destination, replace=args.replace)
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"Falha na recuperação do banco: {error}", file=sys.stderr)
        return 1
    print(f"Arquivo validado criado em: {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
