import click

from .core import ChpipManager

pip_manager = ChpipManager()


@click.group(
    help='A tool to manage the base URL of the Python package index.',
    invoke_without_command=True)
@click.option('-n', '--name', help='Use the Python package index with the specified name.')
@click.pass_context
def cli(ctx, name=None):
    if ctx.invoked_subcommand is None:
        pip_manager.change_index(name)


@cli.command()
@click.option('-n', '--name', help='Name of the Python package index.')
@click.option('-i', '--index-url',
              help='Base URL of the Python Package Index (default https://pypi.org/simple). '
                   'This should point to a repository compliant with PEP 503 (the simple repository API) '
                   'or a local directory laid out in the same format.')
def set(name, index_url):
    pip_manager.set_index(name, index_url)


if __name__ == '__main__':
    cli()
