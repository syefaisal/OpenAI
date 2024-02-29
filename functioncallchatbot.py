import json
import streamlit as st
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import time
import config

openai_api_key = config.OPENAI_API_KEY
llm_model = config.LLM_MODEL
GPT_MODEL = llm_model
client = OpenAI(api_key=openai_api_key)
# st.title("Function Call Chatbot")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#     st.session_state.messages.append(
#         {"role": "assistant", "content": "Hi, how can I assist you today?"})

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("Message QA Chatbot..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""

#     query = [msg["content"]
#              for msg in st.session_state.messages if msg["role"] == "user"][-1].lower()

    
#     assistant_response = chat_completion_request(
#         st.session_state.messages, tools=tools
#     )

    # # Simulate stream of response with milliseconds delay
    # if "\n" in assistant_response:
    #     for chunk in assistant_response.split("\n"):
    #         for item in chunk.split():
    #             full_response += item + " "
    #             time.sleep(0.05)
    #             # Add a blinking cursor to simulate typing
    #             message_placeholder.markdown(full_response + "▌")
    #         full_response += "\n"
    # else:
    #     for item in assistant_response.split():
    #         full_response += item + " "
    #         time.sleep(0.05)
    #         # Add a blinking cursor to simulate typing
    #         message_placeholder.markdown(full_response + "▌")

    # message_placeholder.markdown(assistant_response)

    # # Add assistant response to chat history
    # st.session_state.messages.append(
    #     {"role": "assistant", "content": full_response})


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }

    for messages in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] =="user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] =="assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] =="assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


def main():
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": "What's the weather like today in Glasgow, Scotland."})
    
    chat_response = chat_completion_request(
        messages, tools=tools
    )
    assistant_message = chat_response.choices[0].message
    messages.append(assistant_message)
    print(assistant_message)



main()


st.title("Function Call Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hi, how can I assist you today?"})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message QA Chatbot..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    query = [msg["content"]
             for msg in st.session_state.messages if msg["role"] == "user"][-1].lower()

    
    chat_response = chat_completion_request(
        st.session_state.messages, tools=tools
    )
    assistant_message = chat_response.choices[0].message
    if assistant_message.tool_calls:
        assistant_message.content = str(assistant_message.tool_calls[0].function)
    assistant_response = assistant_message.content
    
    for item in assistant_response.split():
        full_response += item + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    
    message_placeholder.markdown(assistant_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
