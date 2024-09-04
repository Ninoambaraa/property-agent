import streamlit as st
import time
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# db = SQLDatabase.from_uri("sqlite:///Chinook.db")
db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:qzjHK3GZvglMHv3TM4QynrMQuB4cZJx6d8xGq19CZfdyAl2Byn2Gt3dE9SEt6eKS@84.247.149.184:5432/property")
print(db.dialect)
print(db.get_usable_table_names())

system = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool! 

You have access to the following tables: {table_names}

You have to provide the most important 3 fields, namely name, price and address

If the question does not seem related to the database, just return "There's no data about that , i'm so sorry" as the answer."""

prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "{input}"), MessagesPlaceholder("agent_scratchpad")]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_sql_agent(
    llm=llm,
    db=db,
    prompt=prompt,
    verbose=True,
    agent_type="openai-tools",
)


# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamed response emulator (This now processes the whole formatted message instead of word by word)
def format_property_response(response):
    # Formatting response as a markdown block for readability
    formatted_response = ""
    properties = response.get("properties", [])

    if not properties:
        return "No properties available."

    formatted_response += "The top properties available are:\n\n"
    for i, prop in enumerate(properties, start=1):
        formatted_response += f"**{i}. Title:** {prop['title']}\n"
        formatted_response += f"**Price:** {prop['price']}\n"
        formatted_response += f"**Address:** {prop['address']}\n\n"

    return formatted_response

# Main Streamlit app
st.title("Property Agent 🏡")
st.text("It will help you, I promise")
st.text("Try Ask 'What are the top 3 properties available?'")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Invoke the agent and fetch response
    result = agent.invoke({"input": prompt})
    
    # Assuming the agent returns a dict with 'output' as key containing property list
    response_data = result['output']
    # formatted_response = format_property_response(response_data)

    # Display the assistant's response with proper formatting
    with st.chat_message("assistant"):
        st.markdown(response_data)

    st.session_state.messages.append({"role": "assistant", "content": response_data})
