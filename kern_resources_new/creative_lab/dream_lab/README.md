# Dream Lab

A module for AI dreaming and continuous learning in the Kern Resources project.

## Overview

Dream Lab implements a system for AI dreaming and continuous learning, inspired by how human dreaming helps process information and enhance creativity. The system uses a dual-track approach:

1. **Operational Team**: An Instruct AI model leads a team of expert models for normal operations
2. **Learning Base Model**: A base model participates in the team and simultaneously undergoes continuous learning
3. **Dream-like Exploration**: During downtime, the system engages in creative exploration and problem-solving
4. **Self-Reflection**: The system reflects on its experiences and learns from them

## Directory Structure

```
dream_lab/
├── agents/          # Agent definitions
├── memory/          # Memory and reflection system
├── training/        # Fine-tuning components
├── exploration/     # Dream-time task generation
├── orchestration/   # Multi-agent coordination
└── integration.py   # Integration with main application
```

## Components

### Agents

The `agents` module defines the multi-agent team:

- **Lead Model**: An instruction-following model that coordinates the team
- **Expert Models**: Specialized models for different domains
- **Base Model**: A model that learns from the team's experiences

### Memory

The `memory` module manages the system's experiences and reflections:

- Stores experiences from tasks
- Generates reflections on experiences
- Retrieves relevant memories for future tasks

### Training

The `training` module handles the continuous learning of the base model:

- Collects training examples from team interactions
- Prepares datasets for fine-tuning
- Schedules fine-tuning jobs

### Exploration

The `exploration` module generates tasks for dream-time exploration:

- Creates creative and exploratory tasks
- Focuses on different resource types and demographic groups
- Generates batches of tasks for dream sessions

### Orchestration

The `orchestration` module coordinates the dream-time activities:

- Schedules dream sessions during downtime
- Manages the dream process
- Triggers fine-tuning when enough data is collected

## Usage

### Initialization

```python
from creative_lab.dream_lab.integration import init_dream_lab

# Initialize Dream Lab
dream_team, dream_scheduler = init_dream_lab(app)

# Start scheduled dreaming
dream_scheduler.start_scheduled_dreaming()
```

### Manual Dream Session

```python
# Trigger a dream session
dream_scheduler.trigger_dream_session()
```

### Solving Tasks

```python
# Solve a task using the dream team
result = dream_team.solve_task("Find housing resources for seniors in Kern County")
```

### Retrieving Memories

```python
# Retrieve relevant memories
memories = dream_scheduler.memory_system.retrieve_relevant_memories("housing seniors")
```

## API Endpoints

When integrated with a Flask application, Dream Lab provides the following API endpoints:

- `GET /api/dream_lab/status`: Get the current status of the dream lab
- `POST /api/dream_lab/trigger_dream`: Manually trigger a dream session
- `GET /api/dream_lab/memories`: Get relevant memories based on a query
- `GET /api/dream_lab/training/stats`: Get statistics about the training data
- `POST /api/dream_lab/solve`: Solve a task using the dream team

## CLI Commands

Dream Lab also provides CLI commands for managing dream lab operations:

```bash
# Show the current status of the dream lab
flask dream status

# Manually trigger a dream session
flask dream trigger

# List memories matching a query
flask dream memories --query "housing" --limit 10
```

## Configuration

Dream Lab can be configured through the `DREAM_LAB_CONFIG` dictionary in the Flask application configuration:

```python
app.config['DREAM_LAB_CONFIG'] = {
    'memory_path': 'data/dream_lab/memories',
    'training_data_path': 'data/dream_lab/training',
    'min_examples_for_training': 50,
    'auto_schedule_dreams': True,
    'dream_time': '02:00',
    'dream_duration': 60,
    'dream_task_count': 3,
    'downtime_start_hour': 22,
    'downtime_end_hour': 6
}
```

## Dependencies

- CrewAI (optional): For multi-agent orchestration
- Flask (optional): For API endpoints and CLI commands
- Schedule (optional): For scheduling dream sessions
