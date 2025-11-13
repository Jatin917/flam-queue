# main.py
from cli import build_cli
from storage import Storage
from config import Config


def main():
    storage = Storage()
    cfg = Config.load()
    cli = build_cli(storage=storage, config=cfg)
    cli()


if __name__ == "__main__":
    main()