#!/bin/bash

# Ralph Wiggum Autonomous Execution Wrapper: "I'm helping!"

if [ -z "$1" ]; then
    echo "Usage: ./ralph_loop.sh <task_id>"
    exit 1
fi

TASK_ID=$1
MAX_ITERATIONS=${2:-5}

echo "Running Ralph Wiggum Autonomous Task Loop for task: $TASK_ID"
python3 AI_Employee/orchestrator/ralph_loop.py "$TASK_ID" "$MAX_ITERATIONS"
