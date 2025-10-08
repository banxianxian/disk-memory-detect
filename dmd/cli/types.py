import argparse


class CLISubcommand(object):
    name: str
    @staticmethod
    def cmd(args: argparse.Namespace) -> None:
        raise NotImplementedError("cli.types Subclasses should implement this method")

    def validate(self, args: argparse.Namespace) -> None:
        pass

    def subparser_init(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        raise NotImplementedError("cli.types Subclasses should implement this method")