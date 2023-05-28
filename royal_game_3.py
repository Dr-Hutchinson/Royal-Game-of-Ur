import streamlit as st
import streamlit.components.v1 as components
from streamlit_chat import message
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.document_loaders import YoutubeLoader
from langchain.indexes import VectorstoreIndexCreator
import os
import openai

os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]
openai.api_key = os.getenv("OPENAI_API_KEY")

with st.expander('Youtube Video:'):
    # The URL of the YouTube video
    video_url = "https://youtu.be/wHjznvH54Cw"

    # Display the video player
    st.video(video_url)


with st.expander('Cuniform Tablet featuring Royal Game of Ur from the British Library:'):

    # The URL of the image from the British Museum website
    image_url = "http://media.britishmuseum.org/media/Repository/Documents/2014_11/12_20/f8d09bf3_a156_4a95_befc_a3e101544e67/preview_00129985_001.jpg"

    # Create an HTML hyperlink around the image
    # The URL of the image from the British Museum website

    # Display the image as an iframe
    st.image(image_url)


with st.expander("Play the Royal Game of Ur"):
    components.iframe("https://royalur.net/", width=800, height=600)

# Load the YouTube transcript
loader = YoutubeLoader.from_youtube_url("https://youtu.be/wHjznvH54Cw", add_video_info=False, language='en-GB')

# Create an index from the loader
index = VectorstoreIndexCreator().from_loaders([loader])

with st.expander("Chat about the Royal Game of Ur"):

    # Define the prompt template
    template = """Assistant is a large language model trained by OpenAI.
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    {history}
    Human: {human_input}
    Assistant:"""

    prompt = PromptTemplate(
     input_variables=["history", "human_input"],
     template=template
    )

    # Create the LLMChain
    chatgpt_chain = LLMChain(
     llm=OpenAI(temperature=0),
     prompt=prompt,
     verbose=True,
     memory=ConversationBufferWindowMemory(k=2),
    )

    # Initialize the conversation history
    if 'history' not in st.session_state:
        st.session_state.history = ""

    # Display the initial messages
    message("Messages from the bot", key="message_0")
    message("Your messages", is_user=True, key="message_1")  # align's the message to the right

    # Display the conversation
    if st.session_state.history:
        for i, line in enumerate(st.session_state.history.split('\n')):
            if line.startswith('Human:'):
                message(line[6:], is_user=True, key=f"message_{i+2}")
            elif line.startswith('Assistant:'):
                message(line[10:], key=f"message_{i+2}")

    # Get user input
    user_input = st.text_input("Enter your message:")

    # Add a button to trigger the model's response
    if st.button("Send"):
        # If the user enters a message
        if user_input:
            # Update the conversation history
            st.session_state.history += f"Human: {user_input}\n"

            # Get the bot's response
            output = chatgpt_chain.predict(human_input=user_input)

            # Query the YouTube transcript
            youtube_response = index.query(user_input)

            # Combine the responses
            output += "\n" + youtube_response

            # Update the conversation history
            st.session_state.history += f"Assistant: {output}\n"

            # Clear the user input
            st.text_input("Enter your message:", value="", key="user_input")

            # Rerun the script to display the new output
            st.experimental_rerun()
