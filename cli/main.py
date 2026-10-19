
import getpass
import json
import os
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = PROJECT_ROOT / "ansible" / "site.yml"


def main():
    host = input("Server IP: ").strip()
    port = input("SSH port: ").strip()
    user = input("SSH username: ").strip()

    postgres_password = getpass.getpass("PostgreSQL password: ")

    vars_path = None

    try:
        # Создаём временный файл с паролем PostgreSQL
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            prefix="pykubedeploy-",
            delete=False,
        ) as file:
            vars_path = file.name
            os.chmod(vars_path, 0o600)
            json.dump(
                {"postgres_password": postgres_password},
                file,
            )

        # Формируем команду запуска Ansible
        command = [
            "ansible-playbook",
            "-i", f"{host},",
            "-u", user,
            "-e", f"ansible_port={port}",
            "-e", "ansible_python_interpreter=/usr/bin/python3",
            "-e", f"@{vars_path}",
            "--ask-pass",
            "--ask-become-pass",
            str(PLAYBOOK),
        ]

        print("\n[INFO] Starting Ansible deployment...\n")

        subprocess.run(command, check=True)

        print("\n[OK] Ansible completed successfully!")

    except subprocess.CalledProcessError as error:
        print(f"\n[ERROR] Ansible failed: {error.returncode}")

    except FileNotFoundError:
        print("\n[ERROR] Ansible is not installed!")

    finally:
        # Удаляем временный файл с паролем
        if vars_path is not None:
            os.unlink(vars_path)


if __name__ == "__main__":
    main()
