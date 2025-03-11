from session_manager import CreativeSession
import click

@click.group()
def cli():
    """Creative Lab CLI Interface"""
    pass

@cli.command()
@click.option('--name', prompt='Session name', help='Name of the creative session')
def new_session(name):
    """Start a new creative session"""
    session = CreativeSession()
    session.start_new_session(name)
    click.echo(f"Created new session: {session.session_id}")

@cli.command()
@click.option('--content', prompt='Conversation content', help='Content to save')
def add_conversation(content):
    """Add a new conversation"""
    session = CreativeSession()
    path = session.save_conversation("cli_user", content)
    click.echo(f"Saved conversation to: {path}")

if __name__ == '__main__':
    cli()