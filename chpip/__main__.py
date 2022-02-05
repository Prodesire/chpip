import sys

import click

from chpip import exception
from chpip.core import ChpipManager

pip_manager = ChpipManager()


@click.group(
    help='A tool to manage the base URL of the Python package index.',
    invoke_without_command=True)
@click.option('-n', '--name', help='Use the Python package index with the specified name.')
@click.pass_context
def cli(ctx, name=None):
    if ctx.invoked_subcommand is None:
        try:
            name = pip_manager.change_index(name)
            click.echo('Change Python package index to `{}` successful.'.format(name))
        except exception.ChpipException as e:
            click.echo(str(e))
            ctx.exit(1)


@cli.command()
@click.option('-n', '--name', required=True, help='Name of the Python package index.')
@click.option('-i', '--index-url',
              required=True,
              help='Base URL of the Python Package Index (default https://pypi.org/simple). '
                   'This should point to a repository compliant with PEP 503 (the simple repository API) '
                   'or a local directory laid out in the same format.')
@click.pass_context
def set(ctx, name, index_url):
    try:
        name = pip_manager.set_index(name, index_url)
        click.echo('Set Python package index with name `{}` successful.'.format(name))
    except exception.ChpipException as e:
        click.echo(str(e))
        ctx.exit(1)


if __name__ == '__main__':
    cli()
