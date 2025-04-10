from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langgraph_supervisor import create_supervisor
from langchain import hub as prompts
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.utils.config import get_store

from code_mentor_supervisor.configuration import Configuration, ConfigSchema
from code_mentor_supervisor.prompts import solver_prompt, mentor_prompt, supervisor_prompt
from code_mentor_supervisor.utils import fetch_doc

async def supervisor_prompt_with_memories(state):
    """Prepare the messages for the supervisor with memories."""
    # Get store from configured contextvar
    store = get_store()  # Same as that provided to create_supervisor
    
    # Search for memories relevant to the current conversation
    memories = ""
    if "messages" in state and len(state["messages"]) > 0:
        # Get the latest message content for context
        latest_message = state["messages"][-1].content if state["messages"] else ""
        
        # Search within the same namespace as configured for the agent
        # Use asynchronous search method with a higher limit to ensure we get all relevant memories
        search_results = await store.asearch(
            ("memories",),
            query=latest_message,
            limit=15  # Increased to ensure we capture all relevant memories
        )
        
        if search_results:
            # Extract the content from each SearchItem object
            # SearchItem objects have a 'value' field containing the actual memory content
            formatted_items = []
            for item in search_results:
                # Extract the content from the 'value' field of the SearchItem
                # The actual structure may vary depending on how memories are stored
                if hasattr(item, 'value'):
                    # If the value is a dictionary, you might need to extract a specific field
                    if isinstance(item.value, dict) and 'content' in item.value:
                        content = item.value['content']
                    else:
                        content = str(item.value)
                    
                    # You can include metadata if needed
                    item_str = f"Memory ID: {item.key}\n{content}"
                    formatted_items.append(item_str)
                else:
                    # Fallback for any items without the expected structure
                    formatted_items.append(str(item))
            
            # Join the formatted items
            formatted_results = "\n\n".join(formatted_items)
            
            memories = "==== RETRIEVED MEMORIES ====\n\n" + formatted_results
    
    # Format the supervisor prompt with memories and the full message history
    
    # We still extract the latest message for the {message} placeholder
    message = latest_message if "messages" in state and state["messages"] else ""
    
    # Create the formatted prompt with memories and the specific latest message
    formatted_prompt = supervisor_prompt.format(memories=memories, message=message)
    
    # Return both the formatted system message and the full message history
    return [{"role": "system", "content": formatted_prompt}, *state.get("messages", [])]

def create_agent_app(config: RunnableConfig = None):
    """Create the agent application with the given configuration."""
    # Initialize configuration from RunnableConfig
    configurable = Configuration.from_runnable_config(config)
    
    # Configure store with index for embedding-based search
    store = InMemoryStore(
        index={
            "dims": 1536,  # Dimensions for the embedding
            "embed": "openai:text-embedding-3-small",  # Embedding model
        }
    )
    checkpointer = InMemorySaver
    # LLM
    model = init_chat_model(
        model=configurable.model,
        model_provider=configurable.model_provider,
        temperature=configurable.temperature
    )

    # Solving agent
    # Using Langsmith prompts for testing. Copy from LangSmith prompts repo once testing completed
    solver_prompt_formatted = solver_prompt.format(messages="")  # Provide empty default value for messages placeholder
    #solver_sequence = prompts.pull("code-solver-agent-supervisor", include_model=True)
    #solver_prompt_formatted = solver_sequence.steps[0]
    #solver_model = solver_sequence.last.bound.model_name

    solving_agent = create_react_agent(
        model=model,
        prompt=solver_prompt_formatted,
        tools=[fetch_doc],
        name="solving_agent",
    )

    # Mentor agent
    mentor_prompt_formatted = mentor_prompt.format(messages="")  # Provide empty default value for messages placeholder
    #mentor_sequence = prompts.pull("code-mentor-agent-supervisor", include_model=True)
    #mentor_prompt_formatted = mentor_sequence.steps[0]
    #mentor_model = mentor_sequence.last.bound.model_name

    mentor_agent = create_react_agent(
        model=model,
        prompt=mentor_prompt_formatted,
        tools=[fetch_doc],
        name="mentor_agent",
    )

    # Supervisor agent
    # Using Langsmith prompts for testing. Copy from LangSmith prompts repo once testing completed
    # supervisor_sequence = prompts.pull("code-mentor-supervisor-agent", include_model=True)
    # supervisor_prompt_formatted = supervisor_sequence.steps[0]
    # Instead of directly formatting the prompt, use the function that adds memories
    workflow = create_supervisor(
        [solving_agent, mentor_agent],
        model=model,
        prompt=supervisor_prompt_with_memories,  # Use the function instead of formatted string
        tools=[
            create_manage_memory_tool(namespace=("memories",)),
            create_search_memory_tool(namespace=("memories",)),
        ]
    )
    workflow.config_schema = ConfigSchema
    # Create the agent
    app = workflow.compile(
        checkpointer=checkpointer,
        store=store,
    )
    
    return app

# Default instance to be used as entrypoint in langgraph
app = create_agent_app()