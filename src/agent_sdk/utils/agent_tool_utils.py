"""
Agent to Tool conversion utilities with customizable max_turns.

This module provides utilities to convert agents into tools with custom max_turns settings,
which is not available in the default as_tool method.
"""

from typing import Callable, Awaitable, Any
from agents import Agent, Tool, function_tool, Runner, RunResult
from agents.run_context import RunContextWrapper
from agents.items import ItemHelpers


def create_agent_tool_with_max_turns(
    agent: Agent,
    tool_name: str | None = None,
    tool_description: str | None = None,
    max_turns: int = 30,
    custom_output_extractor: Callable[[RunResult], Awaitable[str]] | None = None,
) -> Tool:
    """
    Transform an agent into a tool with customizable max_turns setting.

    This function provides the same functionality as Agent.as_tool() but allows
    specifying a custom max_turns value for the agent execution.

    Args:
        agent: The agent to convert into a tool
        tool_name: The name of the tool. If not provided, the agent's name will be used.
        tool_description: The description of the tool, which should indicate what it does and
            when to use it. If not provided, uses a default description.
        max_turns: The maximum number of turns the agent can run. Defaults to 30.
        custom_output_extractor: A function that extracts the output from the agent. If not
            provided, the last message from the agent will be used.

    Returns:
        Tool: A function tool that runs the agent with the specified max_turns

    Example:
        ```python
        from src.agent_sdk.utils import create_agent_tool_with_max_turns

        # Create an agent
        my_agent = Agent(name="MyAgent", instructions="...")

        # Convert to tool with custom max_turns
        my_tool = create_agent_tool_with_max_turns(
            agent=my_agent,
            tool_name="my_custom_tool",
            tool_description="My custom agent tool",
            max_turns=50
        )

        # Use in another agent
        main_agent = Agent(
            name="MainAgent",
            tools=[my_tool],
            ...
        )
        ```
    """

    # Generate default tool name if not provided
    if tool_name is None:
        # Transform agent name to function-style naming
        tool_name = agent.name.lower().replace(" ", "_").replace("-", "_")

    # Generate default description if not provided
    if tool_description is None:
        tool_description = f"Executes {agent.name} agent with max_turns={max_turns}"

    @function_tool(
        name_override=tool_name,
        description_override=tool_description,
    )
    async def run_agent_with_custom_max_turns(context: RunContextWrapper, input: str) -> str:
        """
        Internal function that runs the agent with custom max_turns.

        Args:
            context: The run context wrapper
            input: The input string for the agent

        Returns:
            str: The agent's output as a string
        """

        # Run the agent with custom max_turns
        output = await Runner.run(starting_agent=agent, input=input, context=context.context, max_turns=max_turns)  # Custom max_turns setting

        # Extract output using custom extractor if provided
        if custom_output_extractor:
            return await custom_output_extractor(output)

        # Default output extraction: get text from message outputs
        return ItemHelpers.text_message_outputs(output.new_items)

    return run_agent_with_custom_max_turns


def create_multiple_agent_tools_with_max_turns(
    agents_config: list[dict[str, Any]],
) -> list[Tool]:
    """
    Create multiple agent tools with custom max_turns settings.

    Args:
        agents_config: List of dictionaries containing agent configuration.
            Each dict should have keys: 'agent', 'tool_name', 'tool_description', 'max_turns'

    Returns:
        list[Tool]: List of tools created from the agents

    Example:
        ```python
        tools = create_multiple_agent_tools_with_max_turns([
            {
                'agent': agent1,
                'tool_name': 'tool1',
                'tool_description': 'Description 1',
                'max_turns': 20
            },
            {
                'agent': agent2,
                'tool_name': 'tool2',
                'tool_description': 'Description 2',
                'max_turns': 40
            }
        ])
        ```
    """
    tools = []

    for config in agents_config:
        tool = create_agent_tool_with_max_turns(
            agent=config["agent"],
            tool_name=config.get("tool_name"),
            tool_description=config.get("tool_description"),
            max_turns=config.get("max_turns", 30),
            custom_output_extractor=config.get("custom_output_extractor"),
        )
        tools.append(tool)

    return tools
