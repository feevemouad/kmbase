from .config import Config
from .sql.sql_tool import ExtendedSQLDatabaseToolkit
from .sql_db_factory import sql_db_factory

from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from typing import Tuple, Dict
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import MessagesPlaceholder
from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS

from typing import Union
import re

FINAL_ANSWER_ACTION = "Final Answer:"


class ExtendedMRKLOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = self.includes_final_answer(text)
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        action_match = re.search(regex, text, re.DOTALL)
        if action_match:
            if includes_answer:
                raise OutputParserException(
                    "Parsing LLM output produced both a final answer "
                    f"and a parse-able action: {text}"
                )
            action = action_match.group(1).strip()
            action_input = action_match.group(2)
            tool_input = action_input.strip(" ")
            # ensure if its a well formed SQL query we don't remove any trailing " chars
            if tool_input.startswith("SELECT ") is False:
                tool_input = tool_input.strip('"')

            return AgentAction(action, tool_input, text)

        elif includes_answer:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )

        if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`",
                observation="Invalid Format: Missing 'Action:' after 'Thought:'",
                llm_output=text,
                send_to_llm=True,
            )
        elif not re.search(
            r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
        ):
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`",
                observation="Invalid Format:"
                " Missing 'Action Input:' after 'Action:'",
                llm_output=text,
                send_to_llm=True,
            )
        else:
            raise OutputParserException(f"Could not parse LLM output: `{text}`")

    def includes_final_answer(self, text):
        includes_answer = (
            FINAL_ANSWER_ACTION in text or FINAL_ANSWER_ACTION.lower() in text.lower()
        )
        return includes_answer

    @property
    def _type(self) -> str:
        return "mrkl"


def setup_memory() -> Tuple[Dict, ConversationBufferMemory]:
    """
    Sets up memory for the open ai functions agent.
    :return a tuple with the agent keyword pairs and the conversation memory.
    """
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    return agent_kwargs, memory


def init_sql_db_toolkit(cfg) -> SQLDatabaseToolkit:
    db: SQLDatabase = sql_db_factory(cfg)
    toolkit = ExtendedSQLDatabaseToolkit(db=db, llm=cfg.llm)
    return toolkit


def initialize_agent(toolkit: SQLDatabaseToolkit, cfg: Config) -> AgentExecutor:
    agent_executor = create_sql_agent(
        llm=cfg.llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=setup_memory(),
        output_parser=ExtendedMRKLOutputParser(),
        handle_parsing_errors=True

    )
    return agent_executor


def agent_factory(cfg) -> AgentExecutor:
    sql_db_toolkit = init_sql_db_toolkit(cfg)
    agent_executor = initialize_agent(sql_db_toolkit, cfg)
    # agent = agent_executor.agent
    # agent.output_parser = ExtendedMRKLOutputParser()
    return agent_executor


if __name__ == "__main__":
    import yaml
    import os
    
    config_path = '../config/config.yml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    try : 
        os.environ["LANGCHAIN_TRACING_V2"]=config["langsmith"]["LANGCHAIN_TRACING_V2"]
        os.environ["LANGCHAIN_ENDPOINT"]=config["langsmith"]["LANGCHAIN_ENDPOINT"]
        os.environ["LANGCHAIN_API_KEY"]=config["langsmith"]["LANGCHAIN_API_KEY"]
        os.environ["LANGCHAIN_PROJECT"]=config["langsmith"]["LANGCHAIN_PROJECT"]
    except:
        pass
    
    agent_executor = agent_factory()
    result = agent_executor.run("Describe all tables")
    print("result:",result)
