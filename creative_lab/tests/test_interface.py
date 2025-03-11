import pytest
from creative_lab.interface import cli
from click.testing import CliRunner

@pytest.fixture
def runner():
    """Fixture to provide a CLI runner for each test"""
    return CliRunner()

def test_cli_new_session(runner):
    """Test creating a new session via CLI"""
    # Test with option
    result = runner.invoke(cli, ['new-session', '--name', 'test_session'])
    assert result.exit_code == 0
    assert 'Created new session' in result.output
    
    # Test with prompt
    result = runner.invoke(cli, ['new-session'], input='test_session\n')
    assert result.exit_code == 0
    assert 'Created new session' in result.output

def test_cli_add_conversation(runner):
    """Test adding a new conversation via CLI"""
    # Test with option
    result = runner.invoke(cli, ['add-conversation', '--content', 'test content'])
    assert result.exit_code == 0
    assert 'Saved conversation' in result.output
    
    # Test with prompt
    result = runner.invoke(cli, ['add-conversation'], input='test content\n')
    assert result.exit_code == 0
    assert 'Saved conversation' in result.output

def test_cli_error_handling(runner):
    """Test CLI error handling"""
    # Test with empty name
    result = runner.invoke(cli, ['new-session', '--name', ''])
    assert result.exit_code != 0
    
    # Test with empty content
    result = runner.invoke(cli, ['add-conversation', '--content', ''])
    assert result.exit_code != 0

def test_cli_help(runner):
    """Test CLI help messages"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Creative Lab CLI Interface' in result.output
    
    result = runner.invoke(cli, ['new-session', '--help'])
    assert result.exit_code == 0
    assert 'Start a new creative session' in result.output
    
    result = runner.invoke(cli, ['add-conversation', '--help'])
    assert result.exit_code == 0
    assert 'Add a new conversation' in result.output
