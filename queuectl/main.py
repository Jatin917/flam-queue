# main.py
from queuectl.cli import build_cli
from queuectl.storage import Storage
from queuectl.config import Config


def main():
    storage = Storage()
    cfg = Config.load()
    cli = build_cli(storage=storage, config=cfg)
    cli()


if __name__ == "__main__":
    main()