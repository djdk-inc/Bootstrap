import os
import click


@click.group()
def cli():
    pass


@cli.command()
def run():
    """Main task logic."""
    print("Task started")
    # TODO: implement task logic
    print("Task complete")


if __name__ == "__main__":
    cli()
