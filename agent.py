import json
import re
from termcolor import colored
from tools.toolbox import Toolbox

from prompts.system_prompt import agent_system_prompt_template
from prompts.format_prompt import formats
from models.mistral_nemo_instruct_2407 import mistral_nemo_instruct_2407
from models.llama_3_1_70B import llama_3_1_70B
from tools.basic_calculator import basic_calculator
from tools.weather_forecaster import weather_forecaster
from tools.reddit_scrapper import reddit_scrapper
from tools.scrape_tool import scrape_tool
from tools.search_tool import search_tool


class Agent:
    def __init__(self, tools, model, model_name, model_api_key: str | None = None):
        """
        Initializes the agent with a list of tools, a model and the model name.

        Parameters:
        tools (list): List of tool functions.
        model_service (class): The model service class with two methods (first_answer and second_answer).
        model_name (str): The name of the model to use.

        """
        self.tools = tools
        self.model = model
        self.model_name = model_name
        self.model_api_key = model_api_key

    def prepare_tools(self):
        """
        Stores the tools in the toolbox and returns their descriptions.

        Returns:
        str: Descriptions of the tools stored in the toolbox.

        """
        toolbox = Toolbox()
        toolbox.store_tools(self.tools)
        str_tools = toolbox.output_tools()
        return str_tools

    def think(self, prompt):
        """
        Runs the answer methods on the model using the system prompt template and tool descriptions.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        final_answer (list): The response from the model as a list.
        """
        # print("\nPreparing tools...")
        str_tools = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(
            tools=str_tools)
        # print("Tools prepared.")

        model_instance = self.model(
            model_name=self.model_name,
            system_prompt=agent_system_prompt,
            api_key=self.model_api_key
        )

        agent_response_str1 = model_instance.first_answer(prompt)
        agent_response_str1 = agent_response_str1.replace("'", '\'')
        #print(f"My first answer is: {agent_response_str1}.")
        try:
            agent_response_list = json.loads(agent_response_str1)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
        tool_choice = agent_response_list[0]
        format_prompt = formats[tool_choice]

        agent_response_str2 = model_instance.second_answer(
            agent_response_list, format_prompt)
        agent_response_str2 = agent_response_str2.replace("'", '\'')
        corrected_json_string = re.sub(
            r"(?<!\w)'|'(?!\w)", '"', agent_response_str2)
        #print(f"My second answer is: {corrected_json_string}.")
        try:
            agent_response_list = json.loads(corrected_json_string)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")

        return agent_response_list

    def verify_sources(self, search_results, original_query):
        """
        Verify and cross-check search results for consistency and reliability.

        Args:
            search_results (str): The search results to verify
            original_query (str): The original user query

        Returns:
            str: Verification summary with confidence level
        """
        verification_prompt = f"""
You are a fact-checking agent. Analyze these search results for the query "{original_query}":

{search_results}

Please evaluate:
1. Consistency: Do multiple sources agree on key facts?
2. Source quality: Are there reputable sources mentioned?
3. Completeness: Does the information fully address the query?
4. Potential biases or contradictions

Provide a brief verification summary with a confidence level (High/Medium/Low) and highlight any concerns.
"""

        try:
            verification = self.model.first_answer(verification_prompt)
            return f"\n--- Source Verification ---\n{verification}\n--- End Verification ---\n"
        except Exception as e:
            return f"\n--- Verification Error: {str(e)} ---\n"

    def reasoning_step(self, prompt, tool_response, tool_name):
        """
        Add reasoning and verification step for enhanced reliability.

        Args:
            prompt (str): Original user prompt
            tool_response (str): Raw tool response
            tool_name (str): Name of the tool used

        Returns:
            str: Enhanced response with reasoning
        """
        reasoning_prompt = f"""
You are a reasoning agent. The user asked: "{prompt}"

The {tool_name} tool provided this information:
{tool_response}

Please:
1. Analyze the reliability and completeness of this information
2. Identify any potential gaps or uncertainties
3. Suggest if cross-verification might be needed
4. Provide a reasoned assessment of the answer quality

If this is search results, check for consistency between different sources mentioned.
"""

        try:
            reasoning = self.model.first_answer(reasoning_prompt)
            return f"\n--- Reasoning Analysis ---\n{reasoning}\n--- End Analysis ---\n"
        except Exception as e:
            return f"\n--- Reasoning Error: {str(e)} ---\n"

    def execute(self, prompt):
        """
        Execute the agent logic with enhanced reasoning and source verification.

        Args:
            prompt (str): The user prompt

        Returns:
            dict: Structured result for UI with keys: output, tool_name, tool_input
        """
        # First answer: decide which tool to use
        first_response = self.model.first_answer(prompt)
        print(f"My tool response is: {first_response}")

        # Parse the response to extract tool and input
        tool_name = None
        tool_input = None

        for line in first_response.split('\n'):
            if line.strip().startswith('Tool:'):
                tool_name = line.split(':', 1)[1].strip()
            elif line.strip().startswith('My tool input is:'):
                tool_input = line.split(':', 1)[1].strip()

        if not tool_name or not tool_input:
            output = "I couldn't determine which tool to use or what input to provide."
            print(output)
            return {"output": output, "tool_name": None, "tool_input": None}

        # Find and execute the tool
        tool = None
        for t in self.tools:
            if t.__name__ == tool_name:
                tool = t
                break

        if not tool:
            output = f"Tool '{tool_name}' not found."
            print(output)
            return {"output": output, "tool_name": tool_name, "tool_input": tool_input}

        try:
            # Parse tool input
            parsed_input = eval(tool_input)
            print(f"My tool input is: {parsed_input}.")

            # Execute the tool
            response = tool(parsed_input)
            print(f"Tool response: {response}")

            # Enhanced reasoning and verification
            reasoning_analysis = ""
            verification_summary = ""

            # Add reasoning step for all tools
            reasoning_analysis = self.reasoning_step(prompt, response, tool_name)

            # Add source verification specifically for search results
            if tool_name == "search_tool" and "error" not in response.lower():
                verification_summary = self.verify_sources(response, prompt)

            # Second answer: format the response with reasoning
            enhanced_response = response + reasoning_analysis + verification_summary
            final_response = self.model.second_answer(enhanced_response, self.format_prompt)
            print(f"My final response: {final_response}")

            return {
                "output": final_response,
                "tool_name": tool_name,
                "tool_input": parsed_input
            }

        except Exception as e:
            output = f"Error executing tool: {str(e)}"
            print(output)
            return {"output": output, "tool_name": tool_name, "tool_input": tool_input}


if __name__ == "__main__":

    tools = [basic_calculator, weather_forecaster,
             reddit_scrapper, search_tool, scrape_tool]
    model = llama_3_1_70B
    model_name = "llama-3.1-70b-versatile"

    # model = mistral_nemo_instruct_2407
    # model_name = "mistralai/Mistral-Nemo-Instruct-2407"

    agent = Agent(tools=tools, model=model,
                  model_name=model_name,
                  model_api_key=None)

    while True:
        prompt = input(colored("Ask me anything: ", 'cyan'))
        if prompt.lower() == "exit":
            break

        agent.execute(prompt)
