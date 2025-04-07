"""
Integration module for the Dream Lab.

This module provides functions to integrate the Dream Lab with the main application.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Flask
try:
    from flask import Blueprint, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    logger.warning("Flask not available. API endpoints will not be registered.")
    FLASK_AVAILABLE = False
    
    # Create placeholder for Blueprint
    class BlueprintPlaceholder:
        def __init__(self, name, import_name, **kwargs):
            self.name = name
            self.import_name = import_name
            
        def route(self, rule, **options):
            def decorator(f):
                logger.warning(f"Would register route {rule} for function {f.__name__}, but Flask not available")
                return f
            return decorator

# Import Dream Lab components
from .agents.team import DreamTeam
from .exploration.dream_generator import DreamGenerator
from .memory.reflection import MemorySystem
from .training.fine_tuner import BaseLearner
from .orchestration.scheduler import DreamScheduler

# Create blueprint for dream lab API endpoints if Flask is available
if FLASK_AVAILABLE:
    dream_lab_bp = Blueprint('dream_lab', __name__, url_prefix='/api/dream_lab')
else:
    dream_lab_bp = None

# Global instances
dream_team = None
dream_scheduler = None

def init_dream_lab(app=None) -> Tuple[Any, Any]:
    """
    Initialize the dream lab components.
    
    Args:
        app: The Flask application (optional)
        
    Returns:
        A tuple containing the dream team and dream scheduler instances
    """
    global dream_team, dream_scheduler
    
    # Load configuration
    if app:
        config = app.config.get('DREAM_LAB_CONFIG', {})
    else:
        config = {}
    
    # Initialize components
    logger.info("Initializing Dream Lab components")
    
    dream_team = DreamTeam(config)
    dream_generator = DreamGenerator(config)
    memory_system = MemorySystem(config)
    base_learner = BaseLearner(config, dream_team.base_model)
    
    # Create scheduler
    dream_scheduler = DreamScheduler(
        config,
        dream_team,
        dream_generator,
        memory_system,
        base_learner
    )
    
    # Start scheduled dreaming if enabled and app is provided
    if app and config.get('auto_schedule_dreams', True):
        dream_scheduler.start_scheduled_dreaming()
    
    # Register blueprint if Flask is available and app is provided
    if FLASK_AVAILABLE and app:
        app.register_blueprint(dream_lab_bp)
        _register_api_routes()
    
    logger.info("Dream Lab initialization complete")
    return dream_team, dream_scheduler

def _register_api_routes():
    """Register API routes for the Dream Lab."""
    if not FLASK_AVAILABLE or not dream_lab_bp:
        return
    
    @dream_lab_bp.route('/status', methods=['GET'])
    def get_status():
        """Get the status of the dream lab."""
        return jsonify({
            'is_dreaming': dream_scheduler.is_dreaming,
            'is_downtime': dream_scheduler.is_downtime(),
            'dream_thread_active': dream_scheduler.dream_thread is not None,
            'scheduled_dream_time': dream_scheduler.dream_time,
            'dream_duration': dream_scheduler.dream_duration,
            'dream_task_count': dream_scheduler.dream_task_count
        })

    @dream_lab_bp.route('/trigger_dream', methods=['POST'])
    def trigger_dream():
        """Manually trigger a dream session."""
        result = dream_scheduler.trigger_dream_session()
        return jsonify({'message': result})

    @dream_lab_bp.route('/memories', methods=['GET'])
    def get_memories():
        """Get relevant memories based on a query."""
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        memories = dream_scheduler.memory_system.retrieve_relevant_memories(query, limit)
        return jsonify({'memories': memories})
    
    @dream_lab_bp.route('/training/stats', methods=['GET'])
    def get_training_stats():
        """Get statistics about the training data."""
        stats = dream_scheduler.base_learner.get_training_stats()
        return jsonify(stats)
    
    @dream_lab_bp.route('/solve', methods=['POST'])
    def solve_task():
        """Solve a task using the dream team."""
        data = request.json
        task = data.get('task', '')
        
        if not task:
            return jsonify({'error': 'No task provided'}), 400
        
        result = dream_team.solve_task(task)
        return jsonify({'result': result})

def register_cli_commands(app):
    """
    Register CLI commands for the Dream Lab.
    
    Args:
        app: The Flask application
    """
    if not app:
        return
    
    try:
        import click
        from flask.cli import AppGroup
        
        # Create a Flask CLI group
        dream_cli = AppGroup('dream', help='Manage dream lab operations')
        
        @dream_cli.command('status')
        def dream_status():
            """Show the current status of the dream lab."""
            status = dream_scheduler.get_status()
            for key, value in status.items():
                click.echo(f"{key}: {value}")
        
        @dream_cli.command('trigger')
        def trigger_dream():
            """Manually trigger a dream session."""
            result = dream_scheduler.trigger_dream_session()
            click.echo(result)
        
        @dream_cli.command('memories')
        @click.option('--query', default='', help='Search query for memories')
        @click.option('--limit', default=5, help='Maximum number of memories to return')
        def list_memories(query, limit):
            """List memories matching a query."""
            memories = dream_scheduler.memory_system.retrieve_relevant_memories(query, limit)
            for memory in memories:
                click.echo(f"Memory: {memory['timestamp']}")
                click.echo(f"Task: {memory['task'][:100]}...")
                click.echo(f"Result: {memory['result'][:100]}...")
                click.echo("---")
        
        # Register the CLI group with the app
        app.cli.add_command(dream_cli)
        
    except ImportError:
        logger.warning("Click or Flask CLI not available. CLI commands will not be registered.")
