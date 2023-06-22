import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.app_logo import add_logo
from streamlit_chat import message
import streamlit_authenticator as stauth
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.document_loaders import YoutubeLoader, BSHTMLLoader, WikipediaLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback
from langchain.agents import initialize_agent, Tool, AgentType
import os
import openai
import pygsheets
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import pandas as pd
import pydeck as pdk
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
from datetime import datetime as dt
import random
import tiktoken
import re

st.set_page_config(layout="wide")

os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]
openai.api_key = os.getenv("OPENAI_API_KEY")

os.environ["MAPBOX_API_KEY"] = st.secrets["mapbox_api_key"]
mapbox_api_key = os.getenv("MAPBOX_API_KEY")

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
gc = pygsheets.authorize(custom_credentials=credentials)





#login setup for streamlit_authenticator via Google Sheets API
sh0 = gc.open('ur_users')
wks0 = sh0[0]
database_length = wks0.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
end_row0 = str(len(database_length))
usernames_grab = wks0.get_as_df(has_header=False, index_column=0, start='A2', end=('A'+end_row0), numerize=False)
usernames_list = usernames_grab.values.tolist()
access_grab= wks0.get_as_df(has_header=False, index_column=0, start='B2', end=('B'+end_row0), numerize=False)
access_list = access_grab.values.tolist()
names_grab = wks0.get_as_df(has_header=False, index_column=0, start='C2', end=('C'+end_row0), numerize=False)
names_list = names_grab.values.tolist()
user_id_grab = wks0.get_as_df(has_header=False, index_column=0, start='D2', end=('D'+end_row0), numerize=False)
user_id_list = names_grab.values.tolist()

#streamlit_authenticator login
names =  [lst[0] for lst in names_list]
usernames = [lst[0] for lst in usernames_list]
passwords = [lst[0] for lst in access_list]
user_ids = [lst[0] for lst in user_id_list]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=300)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write('Welcome *%s*' % (name))

    col1, col2 = st.columns(2)


    with col1:
        with st.expander("Map showing locations discussed in this assignment."):
            #df = pd.DataFrame({
            #'lat': [30.961653],
            #'lon': [46.105126]
            #})
            #Display the map
            #st.map(df)
            # Define the initial viewport
            view_state = pdk.ViewState(
             latitude=30.961653,
             longitude=46.105126,
             zoom=16
            )


            # Original - Define the data for the marker
            #data = pd.DataFrame({
                #'Latitude': [30.961653],
                #'Longitude': [46.105126]
            #})

            #data = pd.DataFrame({
                #'Latitude': [30.961653],
                #'Longitude': [46.105126],
                #'tooltip': [
                #    "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares4.jpg' width='400px'><br><b>Gameboard unearthed for the royal tombs of Ur, c. 2500 BC. British Museum.</b>"
                #]
            #})


            data = pd.DataFrame({
                'Latitude': [30.961653, 30.96280643093184, 30.96202874549048],
                'Longitude': [46.105126, 46.10317429335713, 46.1047200717481],
                'tooltip': [
                    "<img src='https://media.britishmuseum.org/media/Repository/Documents/2017_8/17_15/d63be997_915e_4d23_8bd6_a7d200fd2537/mid_WCO24357__1.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Gameboard unearthed from the Royal Tombs of Ur, c. 2500 BC. British Museum.</b>",
                    "<img src='https://www.re-thinkingthefuture.com/wp-content/uploads/2022/11/A8522-An-Overview-of-The-Ziggurat-of-Ur-Image-6.jpg' width='400px' height='400px'><div style='word-wrap: break-word; width: 300px;'><br><b>Ziggurat of Ur, built c. 21st century BC.</b>",
                    "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Royal_Cemetery_of_Ur_excavations_%28B%26W%29.jpg/1280px-Royal_Cemetery_of_Ur_excavations_%28B%26W%29.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Excavation of the Royal Tombs of Ur, 1920's (AD).</b>"
                ]
            })

            # Define the icon data
            icon_data = {"url":"https://img.icons8.com/plasticine/100/000000/marker.png", "width":128, "height":128, "anchorY":128}
            # Add the icon data to the dataframe
            #data["icon"] = [icon_data]
            data["icon"] = [icon_data for _ in range(len(data))]
            # Define the layer to add to the map
            layer = pdk.Layer(
                type="IconLayer",
                data=data,
                get_icon="icon",
                get_size=4,  # Adjust size as needed
                size_scale=15,  # Adjust scale as needed
                get_position=["Longitude", "Latitude"],
                pickable=True,
            )
            # Let the user toggle between map styles
            is_satellite = st.checkbox('Show satellite view', value=True)
            if is_satellite:
                map_style = 'mapbox://styles/mapbox/satellite-v9'
            else:
                map_style = 'mapbox://styles/mapbox/streets-v11'

            tooltip={
                "html": "{tooltip}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
            # Define the map
            r = pdk.Deck(
             map_style=map_style,
             initial_view_state=view_state,
             layers=[layer],  # Add the layer to the map
             tooltip=tooltip
            )
            # Display the map
            st.pydeck_chart(r)


        with st.expander("Exploring Ur"):

            def ziggurat_of_ur():

                st.header("Exploring the Ziggurat of Ur")

                st.write("The Ziggurat of Ur, an architectural marvel of the ancient world, stands as a testament to the power, ingenuity, and cultural richness of the civilization that built it. Constructed around 2100 B.C.E. under the rule of King Ur-Nammu, the ziggurat was dedicated to the moon goddess Nanna, the patron deity of Ur. This massive structure, rising from the flat landscape, was the highest point in the city, serving as a beacon for travelers and a focal point for the city's inhabitants.")

                image_url_0 = "https://ychef.files.bbci.co.uk/976x549/p0cv0dsc.jpg"
                st.image(image_url_0, caption="""Photo of the Ziggurat of Ur.""")

                st.write("Architecturally, the ziggurat was a marvel of engineering. Its core was made of mud brick, covered with a protective layer of baked bricks laid with bitumen, a naturally occurring tar.")

                image_url_1 = "https://upload.wikimedia.org/wikipedia/commons/c/cf/OLD_tar_%28like_our_cement_or_mortar%29_but_2500_-_6000_y.o..JPG"
                st.image(image_url_1, caption="""Photo of Ur's ruins featuring the use of bitumin, or tar, to keep the stones "glued" into place.""")

                st.write("The structure was tiered, with each level smaller than the one below, creating a stepped pyramid. The architects incorporated functional elements into the design, including holes through the baked exterior layer to allow water to evaporate from its core, and built-in drainage systems on the terraces to carry away the winter rains. This attention to detail and practicality speaks to the advanced engineering skills of the people of Ur.")

                ziggurat_video = "https://youtu.be/Im4jNuYmYjQ"
                st.video(ziggurat_video)

                st.write("Religiously, the Ziggurat of Ur was the city's spiritual heart. It was a place of worship, a home for the city's patron deity, and a site for important religious rituals. The ziggurat's towering presence would have served as a constant reminder of the city's devotion to Nanna. This religious significance is mirrored in the Royal Game of Ur, which was found in the Royal Cemetery of Ur and may have held a significant role in the city's religious or ritualistic practices.")

                st.write("Politically, the construction of the Ziggurat of Ur reflects the power and authority of the city's rulers. The ability to mobilize the resources and labor necessary to build such a massive structure demonstrates the political strength of the ruling class. The ziggurat, visible from miles around, would have served as a symbol of the city's power and the might of its rulers.")

                image_url_2 = "http://media.britishmuseum.org/media/Repository/Documents/2014_9/29_16/7a023097_f82a_46b5_9026_a3b501161417/preview_00146467_001.jpg"
                st.image(image_url_2, caption="Cuniform stamp on a brick used at Ur with the royal emblem of Ur-Nammu. British Museum.")

                st.write("Socially, the ziggurat reinforced the city's social hierarchy. Its grandeur and prominence would have been a constant reminder of the social order, with the city's rulers and gods at the top. The ziggurat's role as a center for religious, administrative, and possibly even economic activities would have made it a hub of city life, reflecting the city's social structure.")

                st.write("Historically and culturally, the Ziggurat of Ur is a significant artifact that sheds light on the achievements of the Ancient Near East. Its construction demonstrates advanced architectural and engineering skills, while its role in the city's religious and social life speaks to the cultural richness of this civilization. The connection to the Royal Game of Ur further underscores this cultural richness, offering insights into the city's religious practices, social structure, and material culture.")

                st.write("The Ziggurat of Ur and the Royal Game of Ur are intertwined in their reflection of the city's religious, political, social, and cultural life. The game, found in the nearby royal tombs, may have been used in rituals or as a symbolic object, much like the ziggurat was a stage for religious rituals. Moreover, both the game and the ziggurat reflect the city's wealth and the craftsmanship of its artisans, providing insights into the material culture of Ur. Both artifacts offer valuable insights into the civilization that created them, revealing a society marked by advanced engineering skills, complex social structures, and a rich cultural and religious life")

            quiz_choice = st.selectbox("Choose Exploration:", ['Ziggurat of Ur'])

            if quiz_choice == 'Ziggurat of Ur':
                ziggurat_of_ur()

    with col2:
        with st.expander("Complete Assignments"):

            #def geoquiz():

            #    st.title("GeoQuiz")

            #    st.header("Placeholder")

            #    st.header("Chatbot Interface:")

            #    colored_header(
            #        label="",
            #        description="\n\n",
            #        color_name="violet-70",
            #    )

            #    sh1 = gc.open('ur_quiz_questions')
            #    wks1 = sh1[0]
            #    df_quiz_source = wks1.get_as_df()

                # Randomly sample questions from the DataFrame
            #    df_sample = df_quiz_source.sample(n=3)  # replace 10 with the number of questions you want in the quiz

                # Store the sampled DataFrame in the session state
            #    st.session_state.df_sample = df_sample

                # Create a form
            #    with st.form(key='quiz_form'):
                    # Loop through the sampled DataFrame and display questions
            #        for index, row in df_sample.iterrows():
            #            st.write(f"Question {row['question_number']}: {row['question']}")

                        # Check if it's a True/False question
            #            if pd.isnull(row['option_3']):
            #                options = ['True', 'False']
            #            else:
            #                options = [row['option_1'], row['option_2'], row['option_3'], row['option_4'], row['option_5']]

                        # Display options as radio buttons and store the user's answer in the session state
                        # Use different keys for st.session_state and st.radio
            #            st.session_state[f"answer_{row['question_number']}"] = st.radio("Select your answer:", options, key=str(row['question_number']))

                    # Add a submit button to the form
            #        if st.form_submit_button(label='Submit Answers'):
            #            st.session_state.submitted = True

                # Function to check the answers
            #    def check_answers():
            #        for question_number in st.session_state.df_sample['question_number']:
            #            user_answer = st.session_state[f"answer_{question_number}"]
            #            correct_answer = st.session_state.df_sample.loc[st.session_state.df_sample['question_number'] == question_number, 'answer'].values[0]
            #            if user_answer == str(correct_answer):
            #                st.write(f"Question {question_number}: Correct!")
            #            else:
            #                st.write(f"Question {question_number}: Incorrect. The correct answer is: " + str(correct_answer))

                # Check the answers when the submit button is clicked
            #    if 'df_sample' in st.session_state and st.session_state.submitted:
            #        check_answers()
                #if st.button('Reset Chat History'):
                    #st.session_state['requests'] = []
                    #st.session_state['responses'] = ["How can I assist you?"]
                    #st.session_state['sources'] = []
                    #st.session_state['token_count'] = []
                    #st.experimental_rerun()

                #if 'token_count' not in st.session_state:
                    #st.session_state['token_count'] = []

                #if 'responses' not in st.session_state:
                #    st.session_state['responses'] = ["How can I assist you?"]

                #if 'requests' not in st.session_state:
                #    st.session_state['requests'] = []

                #llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets["openai_api_key"])

                #if 'buffer_memory' not in st.session_state:
                #    st.session_state.buffer_memory=ConversationBufferWindowMemory(k=1,return_messages=True)

                #def get_conversation_string():
                #    conversation_string = ""
                #    for i in range(len(st.session_state['responses'])-1):
                #        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
                #        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
                #    return conversation_string

                #prompt = "Compose a response based on the user input."

                #system_msg_template = SystemMessagePromptTemplate.from_template(template=prompt)

                #human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

                #prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

                #conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

                # token counting script
                #encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

                #def count_tokens(chain, query):
                #    with get_openai_callback() as cb:
                #        result = chain.predict(input=query)
                #        print(f'Spent a total of {cb.total_tokens} tokens')
                #        st.session_state.token_count.append(cb.total_tokens)
                #        return result, cb.total_tokens

                #token_counts = []

                # container for chat history
                #response_container = st.container()
                # container for text box
                #textcontainer = st.container()

                #with textcontainer:
                #    with st.form(key='chat_form'):
                #        query = st.text_input("Enter your question to the chatbot here: ", key="input")
                #        submit_button = st.form_submit_button(label='Submit Question')
                #        if submit_button and query is not None and query != "":
                #            with st.spinner("Getting Response..."):


                #                conversation_string = get_conversation_string()

                #                response, tokens = count_tokens(conversation, f"Here are your data sources:\n {conversation_string} \n\Respond in the manner requested by the user. Extract only the relevant details from the data sources, and avoid repetition. Use direct quotes from these relevant details to answer this user input:\n\n{query}\n\nIf you don't have relevant information from the sources to answer that, say so.")

                #                st.write("Token Count= " + str(st.session_state.token_count))




            def self_grading_chatbot():

                st.title("Ziggurat of Ur")

                colored_header(
                    label="",
                    description="\n\n",
                    color_name="violet-70",
                )

                if st.button('Reset Chat History'):
                    st.session_state['requests'] = []
                    st.session_state['responses'] = ["Hello, I'm Clio! Enter /start to begin the assignment!"]
                    st.session_state['sources'] = []
                    st.session_state['token_count'] = []
                    st.session_state['questions'] = []
                    st.session_state['question_number'] = 1
                    st.experimental_rerun()

                if 'token_count' not in st.session_state:
                    st.session_state['token_count'] = []

                token_count = []
                st.write(st.session_state.token_count)

                if 'responses' not in st.session_state:
                    st.session_state['responses'] = ["Hello, I'm Clio! Enter /start to begin the assignment!"]

                if 'requests' not in st.session_state:
                    st.session_state['requests'] = []

                if 'sources' not in st.session_state:
                    st.session_state['sources'] = []

                if 'questions' not in st.session_state:
                    st.session_state['questions'] = []

                if 'question_number' not in st.session_state:
                    st.session_state['question_number'] = 1

                if 'answer' not in st.session_state:
                    st.session_state['answer'] = None

                llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=st.secrets["openai_api_key"])

                if 'buffer_memory' not in st.session_state:
                    st.session_state.buffer_memory=ConversationBufferWindowMemory(k=4,return_messages=True)

                # ORIGINAL - DON'T DELETE
                #def get_conversation_string():
                #    conversation_string = ""
                #    for i in range(len(st.session_state['responses'])-1):
                #        conversation_string += "User: "+st.session_state['requests'][i] + "\n"
                #        conversation_string += "Clio: "+ st.session_state['responses'][i+1] + "\n"
                #    return conversation_string

                ### Revision - also don't delete

                #def get_conversation_string():
                #    conversation_string = ""
                #    for i in range(len(st.session_state['responses'])-1):
                        # Remove the sections enclosed in < > after "Answers:" and "Initial Thought:"
                #        revised_response = re.sub(r'Answers:.*', '', st.session_state['responses'][i+1])
                #        revised_response = re.sub(r'<Initial Thought:.*?>', '', revised_response)

                        # Add the request and the revised response to the conversation string
                #        conversation_string += "User: "+st.session_state['requests'][i] + "\n\n"
                #        conversation_string += "Clio: "+ revised_response + "\n\n"
                #    return conversation_string

                def get_conversation_string():
                    conversation_string = ""
                    for i in range(len(st.session_state['responses'])-1):
                        # Remove the sections enclosed in < > after "Answers:" and "Initial Thought:"
                        revised_response = re.sub(r'Answers:.*', '', st.session_state['responses'][i+1])
                        revised_response = re.sub(r'<Initial Thought:.*?>', '', revised_response)

                        # Add the request and the revised response to the conversation string
                        if i < len(st.session_state['requests']):  # Check if the index exists in 'requests'
                            conversation_string += "User: "+st.session_state['requests'][i] + "\n\n"
                        conversation_string += revised_response + "\n\n"
                    return conversation_string



                # Original working function code - don't delete
                #sh1 = gc.open('ur_data')
                #wks1 = sh1[0]

                #def download_data_from_sheet(spreadsheet):
                #    """Function to download data from the first cell of a Google Spreadsheet."""
                    # Select the first worksheet in the spreadsheet
                #    worksheet = wks1

                    # Get the value of the first cell
                #    cell_value = worksheet.get_value('A1')

                #    return cell_value

                #def upload_data_to_sheet(spreadsheet):
                #    """Function to upload data to the first cell of a Google Spreadsheet."""
                    # Select the first worksheet in the spreadsheet
                #    worksheet = wks1
                    # Set the value of the first cell
                #    worksheet.update_value('A1', '3.14')


                #tools = [
                #    Tool(
                #        name="download_data_from_sheet",
                #        func=download_data_from_sheet,
                #        description="Pulls data from a Google Sheet."
                #    ),
                #    Tool(
                #        name="upload_data_to_sheet",
                #        func=upload_data_to_sheet,
                #        description="Uploads data to a Google Sheet."
                #    )
                #]

                #def execute_function_call(message):
                #    if message["function_call"]["name"] == "download_data_from_sheet":
                #        results = download_data_from_sheet(gc)
                #    elif message["function_call"]["name"] == "upload_data_to_sheet":
                #        results = upload_data_to_sheet(gc)
                #    else:
                #        results = f"Error: function {message['function_call']['name']} does not exist"
                #    return results

                # Open the spreadsheets
                sh_questions = gc.open('true_ziggurat_questions')
                sh_scores = gc.open('ziggurat_scores')

                # Select the first worksheets in the spreadsheets
                wks_questions = sh_questions[0]
                wks_scores = sh_scores[0]

                def Pull_Row(spreadsheet):
                    """Function to pull a random row from a Google Spreadsheet."""
                    # Select the worksheet
                    worksheet = wks_questions

                    # Get the length of the database
                    database_length = worksheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
                    end_row = str(len(database_length))

                    # Get the learning objectives, questions, and answers
                    learning_objectives_grab = worksheet.get_as_df(has_header=False, index_column=0, start='B2', end=('B'+end_row), numerize=False)
                    learning_objectives_list = learning_objectives_grab.values.tolist()
                    question_grab = worksheet.get_as_df(has_header=False, index_column=0, start='C2', end=('C'+end_row), numerize=False)
                    question_list = question_grab.values.tolist()
                    answer_grab = worksheet.get_as_df(has_header=False, index_column=0, start='D2', end=('D'+end_row), numerize=False)
                    answer_list = answer_grab.values.tolist()

                    # Select a random index
                    index = random.randint(0, len(learning_objectives_list) - 1)

                    # Extract the values from the columns "learning_objectives", "question", and "answer"
                    learning_objectives = learning_objectives_list[index][0]  # Extract the string from the list
                    question = question_list[index][0]  # Extract the string from the list
                    answer = answer_list[index][0]  # Extract the string from the list

                    #st.write(learning_objectives)
                    #st.write(question)
                    #st.write(answer)

                    return learning_objectives, question, answer


                user = "danielhutchinson"
                score = 5

                def Upload_Data(spreadsheet, user, score):
                    """Function to upload data to a Google Spreadsheet."""
                    # Select the worksheet
                    worksheet = wks_scores

                    # Get the current date
                    date = dt.now().strftime("%Y-%m-%d")

                    # Create the new row
                    new_row = {"user": user, "score": score, "date": date}

                    # Append the new row to the worksheet
                    worksheet.append_table(list(new_row.values()))

                def Upload_Data_Wrapper(spreadsheet):
                    return Upload_Data(spreadsheet, user, score)

                tools = [
                    Tool(
                        name="Pull_Row",
                        func=Pull_Row,
                        description="Pulls a random row from a Google Sheet called 'ziggurat_questions'."
                    ),
                    Tool(
                        name="Upload_Data",
                        func=Upload_Data_Wrapper,
                        description="Uploads data to a Google Sheet called 'ziggurat_scores'."
                    )
                ]




                prompts = ['self_grading_chatbot', 'tool_enabled_chatbot', 'api_prompt']

                # Use Streamlit's radio button to select a prompt
                selected_prompt = st.radio('Choose a prompt', prompts)

                # Open the selected prompt file and read its contents
                with open("./prompts/" + selected_prompt + ".txt", 'r') as file:
                    prompt = file.read()

                system_msg_template = SystemMessagePromptTemplate.from_template(template=prompt)

                human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

                prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

                # added variables to get agent's memory
                agent_kwargs = {
                    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")]
                }

                memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

                # Initialize the agent with the tools and the OpenAI language model
                agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True, agent_kwargs=agent_kwargs, memory=memory)

                # old conversation code - don't delete
                conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

                # token counting script
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

                def count_tokens(chain, query):
                    with get_openai_callback() as cb:
                        result = chain.predict(input=query)
                        print(f'Spent a total of {cb.total_tokens} tokens')
                        st.session_state.token_count.append(cb.total_tokens)
                        return result, cb.total_tokens

                #token_counts = []

                # container for chat history
                response_container = st.container()
                # container for text box
                textcontainer = st.container()

                ##### ORIGINAL CODE - DON'T DELETE
                #with textcontainer:
                #    with st.form(key='chat_form'):
                #        query = st.text_area("Enter your statement to Clio here: ", key="input")
                #        submit_button = st.form_submit_button(label='Submit Question')
                #        if submit_button and query is not None and query != "":
                #            with st.spinner("Getting Response..."):

                #                conversation_string = get_conversation_string()

                                # original code for running chat dialogue, DON'T DELETE

                #                response, tokens = count_tokens(conversation, f"""{query}\n""")

                                # attempts to implement GPT functions
                                #response, tokens = agent.run(f"""{query}\n""")
                                #response = agent.run(f"""{conversation_string}+\n\n{query}\n""")
                                #st.write(response)


                                # Multi-option chat thread for tools implementation - don't delete

                                #conversation_string = get_conversation_string()

                                # Check if the user input is a command
                                #if query.startswith("/"):
                                    # Check if the command is "/start"
                                #    if query == "/start":
                                        # Dialogue option 0 - for starting chat dialogue
                                #        response, tokens = count_tokens(conversation, f"""{query}\n""")
                                #    else:
                                        # Dialogue option 2 - for command uses
                                #        response = agent.run(f"""{query}\n""")
                                #else:
                                    # Dialogue option 1 - for normal Q&A interactions with chatbot
                                #    response, tokens = count_tokens(conversation, f"""{query}\n\n<begin User-Response-Evaluation mode>\nInitial Thought:Thought:>""")


                                #user_dialogue = re.findall(r'User: (.*)', response)
                                #clio_dialogue = re.findall(r'Clio: (.*)', response)
                                #learning_objective = re.findall(r'Learning Objective: (.*)', response)
                                #question = re.findall(r'Question \d+: (.*)', response)
                                #score = re.findall(r'Score: (.*)', response)

                #                st.write("Token Count= " + str(st.session_state.token_count))


                #                st.session_state.requests.append(query)
                #                st.session_state.responses.append(response)


                with textcontainer:
                    with st.form(key='chat_form'):
                        question_number = st.session_state['question_number']
                        query = st.text_area("Enter your statement to Clio here: ", key="input")
                        submit_button = st.form_submit_button(label='Submit Question')
                        if submit_button and query is not None and query != "":
                            st.session_state.requests.append(query)
                            with st.spinner("Getting Response..."):
                                if query == "/start":
                                    st.session_state.requests.append("/start")
                                    #st.session_state.responses.append("")
                                    # Step 2: Print intro statement
                                    opening_statement = "I'm Clio, your AI tutor for assessing your understanding of the Ziggurat of Ur and its historical significance. We're going to have a dialogue where I ask you a series of questions. If you get the question right we'll move on to the next question. If your response is inaccurate or only partially accurate then I'll ask follow-ups to help you think about how to find the answer. For each accurate answer you get 1 point. For each partially accurate answer you get half a point. Inaccurate answers don’t receive points. Our dialogue ends when all five questions have been posed. A score of 3 successfully earns credit for the assessment. However, if you score all five correctly you gain a special achievement."
                                    st.session_state.responses.append(opening_statement)
                                    # Step 3: Execute Pull Row function
                                    learning_objectives, question, answer = Pull_Row(sh_questions)
                                    st.session_state.sources.append((learning_objectives, question, answer))
                                    st.session_state['answer'] = answer
                                    question_statement = f"-Bot: \n\nQuestion {st.session_state['question_number']}: \n\nLearning Objectives: {learning_objectives}\n\nQuestion: {question}\n"
                                    st.session_state.responses.append(question_statement)
                                    st.session_state['questions'].append(opening_statement + "\n" + question_statement)  # Append the opening statement and the first question to 'questions'
                                    #st.session_state['question_number'] += 1
                                    st.write("Condition: Start")
                                    #conversation_string = get_conversation_string()
                                    #st.write(conversation_string)
                                else:
                                    # Step 4: User input
                                    st.session_state.requests.append(query)
                                    # Step 5: LLM call
                                    conversation_string = get_conversation_string()
                                    answer = st.session_state.get('answer', None)
                                    response = None
                                    if answer is not None:
                                        api_call = f"""{answer}\n\n{query}\n\nQuestion {question_number} Evaluation: """
                                        st.write("API call: " + api_call)
                                        response, tokens = count_tokens(conversation, api_call)
                                    else:
                                        # Handle the case where answer is None
                                        st.write("Please input /start to begin the chat.")
                                    #response, tokens = count_tokens(conversation, f"""{answer}\n\n{query}\n\nQuestion {question_number} Evaluation: """)
                                    st.session_state.responses.append(response)
                                    #st.write("Condition: Accurate")
                                    #st.write(conversation_string)
                                    # Step 6: Interpret LLM output
                                    if re.search(r'\bPartially Accurate\b', response) or re.search(r'\bpartially accurate\b', response):
                                        #st.session_state.requests.append(query)
                                        # Partial credit, continue question/conversation
                                        #Upload_Data(sh_scores, user, 3)
                                        st.write("Condition: Partial")
                                        st.write(conversation_string)
                                    elif re.search(r"\bAccurate\b", response, re.IGNORECASE) or re.search(r"Let['’]s now move on to the next question", response, re.IGNORECASE) or re.search(r"Let['’]s move on to the next question", response, re.IGNORECASE):
                                        #st.session_state.requests.append(query)
                                        # Full credit, next question
                                        #Upload_Data(sh_scores, user, 5)
                                        learning_objectives, question, answer = Pull_Row(sh_questions)
                                        st.session_state['answer'] = answer
                                        st.session_state.sources.append((learning_objectives, question, answer))
                                        st.session_state['question_number'] += 1
                                        #st.session_state.responses.append(f"Bot: \n\nQuestion {st.session_state['question_number']}: \n\nLearning Objectives: {learning_objectives}\n\nQuestion: {question}\n\n")
                                        st.session_state['questions'].append(f"Bot: \n\nQuestion {st.session_state['question_number']}: \n\nLearning Objectives: {learning_objectives}\n\nQuestion: {question}\n\n")
                                        #st.session_state['question_number'] += 1
                                        st.write("Condition: Accurate")
                                        st.write(conversation_string)
                                    elif re.search(r'\bInaccurate\b',response):
                                        #st.session_state.requests.append(query)
                                        # No credit, continue question/conversation
                                        #Upload_Data(sh_scores, user, 0)
                                        st.write("Condition: Inaccurate")
                                        st.write(conversation_string)
                                    else:
                                        #st.session_state.requests.append(query)
                                        # Other Response - continue conversation
                                        st.write("Condition: Else")
                                        st.write(conversation_string)
                                        pass
                #### oRIGINAL - DON'T DELETE
                #with response_container:
                #    if st.session_state['responses']:
                #        for i in range(len(st.session_state['responses'])):
                #            message(st.session_state['responses'][i],key=str(i))
                #            if i < len(st.session_state['requests']):
                #                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

                #with response_container:
                with response_container:
                    if st.session_state['requests']:
                        for i in range(len(st.session_state['requests'])):  # Iterate over the user requests instead of the bot responses
                            message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')  # Display the user request
                            if i < len(st.session_state['responses']):  # Check if a corresponding bot response exists
                                message(st.session_state['responses'][i], key=str(i))  # Display the bot response




                with st.form(key='quiz_form'):
                    st.header("Quiz Submission:")
                    st.write("In the space below, offer your thoughts on the following questions:\n\n**1. The Game of Questions:** What approach did you take to framing your questions? What techniques did you find as most or least effective?\n\n**2. Learning from the Chatbot:** How helpful did you find the chatbot in enhancing your knowledge about the Royal Game of Ur?\n\n**3. AI Accuracy**: How did you assess the accuracy of the chatbot's responses? Based on your comprehension of the assisgnment materials, how well does the AI accurately capture factual information?")
                    st.text_area("Enter your response here.")
                    st.write("""Click on the Submit Quiz button to upload your chat history and quiz response for grading.""" )
                    submit_quiz_button = st.form_submit_button(label='Submit Quiz')
                    if submit_quiz_button:
                        now = dt.now()
                        formatted_history = f"User: {username}\nTime: {now}\n\n" + get_conversation_string()
                        with open('chat_history.txt', 'w') as f:
                            f.write(formatted_history)
                        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
                        drive_service = build('drive', 'v3', credentials=credentials)
                        media = MediaFileUpload('chat_history.txt', mimetype='text/plain')
                        request = drive_service.files().create(media_body=media, body={
                            'name': 'chat_history_zig.txt',
                            'parents': ['1p2ZUQuSclMvFwSEQLleaRQs0tStV_-Mu']
                        })
                        response = request.execute()
                        # Print the response
                        st.write("Quiz Submitted.")


            quiz_choice = st.selectbox("Choose chatbot type", ['Game of Questions', 'GeoQuiz'])

            if quiz_choice == "Game of Questions":
                self_grading_chatbot()
            elif quiz_choice == "GeoQuiz":
                geoquiz()



elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
