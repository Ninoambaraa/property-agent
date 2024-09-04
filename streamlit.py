import streamlit as st
import time
from main import agent  # Import the agent from main.py

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
