import pytest
from interface import cli
from click.testing import CliRunner

def test_cli_new_session():
    runner = CliRunner()
    result = runner.invoke(cli, ['new-session', '--name', 'test_session'])
    assert result.exit_code == 0
    assert 'Created new session' in result.output

def test_cli_add_conversation():
    runner = CliRunner()
    result = runner.invoke(cli, ['add-conversation', '--content', 'test content'])
    assert result.exit_code == 0
    assert 'Saved conversation' in result.output