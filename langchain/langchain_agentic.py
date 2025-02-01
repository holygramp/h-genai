import functools
import operator
from typing import Annotated, Literal, Sequence, TypedDict

from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
# from langchain_experimental.utilities import PythonREPL
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode


# Define the state object passed between nodes in the graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


# Tool definitions
def setup_tools():
    """Set up and return the tools used by the agents."""
    duck_duck_go_tool = DuckDuckGoSearchRun(max_results=5, region='fr-fr') # source = news à tester

    # @tool
    # def python_repl(
    #     code: Annotated[str, "The python code to execute to generate your chart."]
    # ):
    #     """Execute Python code and return the result."""
    #     repl = PythonREPL()
    #     try:
    #         result = repl.run(code)
    #     except BaseException as e:
    #         return f"Failed to execute. Error: {repr(e)}"
    #     result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    #     return (
    #         result_str
    #         + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    #     )

    return [duck_duck_go_tool]


# Agent creation
def create_agent(llm, tools, system_message: str):
    """Create an agent with specified LLM, tools, and system message."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "système",
                "Vous êtes un assistant IA utile, qui collabore avec d'autres assistants."
                "Utilisez les outils fournis pour progresser vers la réponse à la question."
                "Si vous n'êtes pas en mesure de répondre complètement, ce n'est pas grave, un autre assistant doté d'outils différents"
                "vous aidera là où vous vous êtes arrêté. Exécutez ce que vous pouvez pour progresser."
                "Si vous ou l'un des autres assistants avez la réponse finale ou le produit livrable,"
                "préfixez votre réponse par FINAL ANSWER pour que l'équipe sache qu'elle doit s'arrêter."
                "Vous avez accès aux outils suivants :{tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(
        system_message=system_message,
        tool_names=", ".join([tool.name for tool in tools]),
    )
    return prompt | llm.bind_tools(tools)


# Node functions
def agent_node(state, agent, name):
    """Process the state through an agent and return the updated state."""
    result = agent.invoke(state)
    if not isinstance(result, ToolMessage):
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        "sender": name,
    }


def setup_workflow(llm, tools):
    """Set up and return the workflow graph."""
    # Create agents
    research_agent = create_agent(
        llm, tools, "Tu dois fournir une valeur numérique représentant la dette de la ville de Dijon pour l'année 2023"
    )
    chart_agent = create_agent(
        llm, tools, "Tu dois vérifier que la valeur en entrée est une valeur numérique"
    )

    # Create nodes
    research_node = functools.partial(
        agent_node, agent=research_agent, name="Researcher"
    )
    chart_node = functools.partial(
        agent_node, agent=chart_agent, name="chart_generator"
    )
    tool_node = ToolNode(tools)

    # Set up the workflow
    workflow = StateGraph(AgentState)
    workflow.add_node("Researcher", research_node)
    workflow.add_node("chart_generator", chart_node)
    workflow.add_node("call_tool", tool_node)

    # Add edges
    workflow.add_conditional_edges(
        "Researcher",
        router,
        {"continue": "chart_generator", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "chart_generator",
        router,
        {"continue": "Researcher", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "call_tool",
        lambda x: x["sender"],
        {"Researcher": "Researcher", "chart_generator": "chart_generator"},
    )
    workflow.add_edge(START, "Researcher")

    return workflow.compile()


# Router function
def router(state) -> Literal["call_tool", "__end__", "continue"]:
    """Determine the next step in the workflow based on the current state."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        return "__end__"
    return "continue"


# Main execution
def main():
    # Set up the LLM
    # llm = ChatBedrock(
    #     model_id="us.amazon.nova-pro-v1:0",
    #     model_kwargs=dict(temperature=0),
    # )

    llm = ChatBedrock( #create a Bedrock llm client
        model_id="mistral.mistral-large-2407-v1:0", #set the foundation model
        model_kwargs={
            "max_tokens": 512,
            "temperature": 0,
            "p": 0.01,
            "k": 0,
            "stop_sequences": [],
            "return_likelihoods": "NONE"
        },
        region_name="us-west-2",

    )

    # Set up tools
    tools = setup_tools()

    # Set up the workflow
    graph = setup_workflow(llm, tools)

    # Execute the workflow
    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="Recherche la dette de la ville de Dijon pour l'année 2023"
                )
            ],
        },
        {"recursion_limit": 150},
    )

    # Print the results
    for s in events:
        print(s)
        print("----")


if __name__ == "__main__":
    main()
