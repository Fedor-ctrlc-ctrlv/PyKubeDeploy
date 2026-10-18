import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = PROJECT_ROOT / "ansible" / "site.yml"


def main():
    host = input("Server IP: ").strip() 
    port = input("SSH port: ").strip() 
    user = input("SSH username: ").strip()

    command = [
        "ansible-playbook",
        "-i", f"{host},",
        "-u", user,
        "-e", f"ansible_port={port}",
        str(PLAYBOOK),
        "--ask-pass",
    ]

    print("\n[INFO] Starting Ansible deployment...\n")

    try:
        subprocess.run(command, check=True)
        print("\n[OK] Ansible completed successfully!")

    except subprocess.CalledProcessError as error:
        print(f"\n[ERROR] Ansible failed: {error.returncode}")

    except FileNotFoundError:
        print("\n[ERROR] Ansible is not installed!")


if __name__ == "__main__":
    main()