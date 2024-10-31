
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from AgentTools import get_excel_data, search_google, enter_data


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    """
    Represents an agent that interacts with a model and tools based on a state machine graph.

    Attributes:
        system (str): Optional system information.
        graph (StateGraph): State machine graph representing agent's behavior.
        tools (dict): Dictionary of tools available to the agent.
        model (Model): Model used by the agent to process messages.
    """
    def __init__(self, model, tools, prompt):
        """
        Initializes an Agent instance.

        Args:
            model (Model): The model used by the agent.
            tools (list): List of tools available to the agent.
        """
        self.prompt = prompt
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def call_openai(self, state: AgentState):
        """
        Calls the OpenAI model to process messages.

        Args:
            state (AgentState): Current state of the agent.

        Returns:
            dict: Updated state with processed message.
        """
        messages = state['messages']
        if self.prompt:
            messages = [SystemMessage(content=self.prompt)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def exists_action(self, state: AgentState):
        """
        Checks if an action should be taken based on the last message.

        Args:
            state (AgentState): Current state of the agent.

        Returns:
            bool: True if action should be taken, False otherwise.
        """
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def take_action(self, state: AgentState):
        """
        Executes tool calls based on the last message and returns results.

        Args:
            state (AgentState): Current state of the agent.

        Returns:
            dict: Updated state with tool execution results.
        """
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            # print(f"Calling: {t}")
            result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        # print("Back to the model!")
        return {'messages': results}

tool = [get_excel_data, search_google, enter_data]

"""
Find the headquarter address for Infosys and enter the same to the data entry portal. Check if the data is available in your excel. If data is in excel, use the address. If data is NOT in excel, search google and get the information. Company name and address information is in /Users/dheerajhegde/Documents/company.xlsx
"""

"""
Find the headquarter address for LTIMindTree and enter the same to the data entry portal. Check if the data is available in your excel. If data is in excel, use the address. If data is NOT in excel, search google and get the information. Company name and address information is in /Users/dheerajhegde/Documents/company.xlsx
"""

prompt = input()

model = ChatOpenAI(model="gpt-4o")
abot = Agent(model, tool, "You are a automation assistant for the user. Complete the tasks using the tools provided.")

abot.graph.invoke({"messages": [prompt]})