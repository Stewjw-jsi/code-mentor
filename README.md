# Code Mentor Supervisor

A LangGraph-powered application designed to assist programming students through a supervisor-agent architecture that provides guidance without revealing complete solutions.

## Overview

The Code Mentor Supervisor is an intelligent tutoring system that uses a multi-agent approach with LangGraph to help students learn programming. The system utilizes three key components:

1. **Solving Agent**: Solves programming problems to understand their solutions
2. **Mentor Agent**: Provides guided assistance to students without revealing solutions
3. **Supervisor**: Orchestrates the interaction between agents and ensures educational best practices. Commits hints and other relevant student facts to memory.

## Features

- Pedagogically sound approach that guides students without providing direct solutions
- Support for web-based documentation retrieval
- Configurable model providers and parameters
- Built on the LangGraph framework for structured agent interactions
- Memory feature for keeping track of hints.

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`
- OpenAI API key or compatible LLM provider
- By default uses GPT-4o-mini for low cost

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/code-mentor-supervisor.git
   cd code-mentor-supervisor
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Create a `.env` file from the provided template:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API credentials:
   ```
   LANGSMITH_TRACING=<BOOL>
   LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
   LANGSMITH_API_KEY="<ENTER_LANGSMITH_API_KEY>"
   LANGSMITH_PROJECT="<ENTER_LANGSMITH_PROJECT>"
   OPENAI_API_KEY="<ENTER_OPENAI_API_KEY>"
   ```

## Usage

### Test run with LangGraph CLI & LangSmith

Before you are ready to run the application, you can test it with the LangGraph CLI using LangSmith:

```bash
$ langgraph dev
```

This will start a server with the agent defined in `langgraph.json`.

## Configuration

The application can be configured through environment variables or through the `RunnableConfig` parameter:

- `MODEL_PROVIDER`: Provider of the LLM (default: "openai")
- `MODEL`: Name of the LLM to use (default: "gpt-4o-mini")
- `TEMPERATURE`: Temperature setting for the LLM (default: 0.0)

## Architecture

The system is built using a LangGraph supervisor workflow that coordinates between the solving agent and mentor agent. The solving agent understands the problem, while the mentor agent creates the hints to be evaluated by the supervisor. The supervisor ensures that solutions are never revealed directly and communicates with the student, committing hints and other student facts to memory.
