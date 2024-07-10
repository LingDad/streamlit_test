import streamlit as st
import replicate
from openai import OpenAI
import os

st.title("Chat with Her! :robot_face:")

with st.sidebar:
    st.header('Sometimes you can chat with llama without API keys :smile:')
    chat_model = st.selectbox("Her Model", ("llama3-8b", "gpt-3.5-turbo", "gpt-4", "gpt-4o"))

    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''

    if "llama" in chat_model:
        api_key = st.text_input('Enter the Replicate API token', type='password')
        if not (api_key.startswith('r8_') and len(api_key)==40):
            st.warning('Please enter your replicate API token', icon='⚠️')
        else:
            st.session_state['api_key'] = api_key
            os.environ['REPLICATE_API_TOKEN'] = st.session_state['api_key']
            st.success('Chat with her, enjoy!', icon='👉')

    if "gpt" in chat_model:
        api_key = st.text_input('Enter the ChatGPT API Key', type='password')
        if not (api_key.startswith('sk-proj-') and len(api_key)==56):
            st.warning('Please enter your API key', icon='⚠️')
        else:
            st.session_state['api_key'] = api_key
            os.environ['OPENAI_API_KEY'] = st.session_state['api_key']
            st.success('Chat with her, enjoy!', icon='👉')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # chat with LLAMA Model with replicate
        if 'llama' in chat_model:
            input = {
                "prompt": prompt,
                "max_new_tokens": 512,
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            }

            for event in replicate.stream(
                "meta/meta-llama-3-8b-instruct",
                input=input
            ):
                if event.data is not None and event.data != '{}':
                    full_response += event.data
                    message_placeholder.markdown(full_response)

        # chat with openAI Chatgpt model
        if "gpt" in chat_model:
            client = OpenAI()
            for response in client.chat.completions.create(
                model=chat_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                if response.choices[0].delta.content is not None:
                    full_response += response.choices[0].delta.content
                    message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})