import click
from opentdx.doc import main as doc_main


@click.group()
def cli():
    """OpenTDX - TDX stock data client CLI"""
    pass


@cli.command()
def doc():
    """Run interactive documentation"""
    doc_main()


if __name__ == '__main__':
    cli()