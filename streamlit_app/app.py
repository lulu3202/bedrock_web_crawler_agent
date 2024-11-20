# Importing required libraries
import invoke_agent as agenthelper  # Custom module to handle lambda functions for query processing.
import streamlit as st             # Streamlit library to build the interactive web interface.
import json                        # JSON library for parsing and handling JSON data.
import pandas as pd                # Pandas for handling tabular data, especially JSON responses.
from PIL import Image, ImageOps, ImageDraw  # Pillow for image processing and transformations.

# Streamlit page configuration
st.set_page_config(page_title="Webscrape Agent", page_icon=":robot_face:", layout="wide") 
# Configures the Streamlit app with a title, an icon, and a wide layout for better visualization.

# Function to crop an image into a circular shape
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)  # Creates a blank mask for the image with the same dimensions.
    mask_draw = ImageDraw.Draw(mask)     # Initializes a drawing context for the mask.
    mask_draw.ellipse((0, 0) + image.size, fill=255)  # Draws a white ellipse on the mask.
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))  # Fits the image to the mask dimensions.
    result.putalpha(mask)  # Adds the circular mask as an alpha channel (transparency).
    return result

# Displaying the app title
st.title("Webscrape Agent")  # Displays the title of the web application.

# Input box for user queries
prompt = st.text_input("Please enter your query?", max_chars=2000)  # Creates a text input box for user queries.
prompt = prompt.strip()  # Strips any extra whitespace from the user input.

# Buttons for user actions
submit_button = st.button("Submit", type="primary")  # Button for submitting the query.
end_session_button = st.button("End Session")        # Button to end the session.

# Sidebar configuration for displaying trace data
st.sidebar.title("Trace Data")  # Adds a title to the sidebar.

# Initialize session state to store conversation history
if 'history' not in st.session_state:
    st.session_state['history'] = []  # Initializes the `history` list if it doesn't already exist.

# Function to format the response received from the agent
def format_response(response_body):
    try:
        data = json.loads(response_body)  # Tries to parse the response body as JSON.
        if isinstance(data, list):       # If the parsed data is a list, convert it to a DataFrame.
            return pd.DataFrame(data)
        else:
            return response_body         # Return the raw response if it's not a list.
    except json.JSONDecodeError:
        return response_body             # Return the raw response if JSON decoding fails.

# Handling query submission
if submit_button and prompt:  # If the submit button is clicked and there’s user input:
    event = {
        "sessionId": "MYSESSION",       # Example session ID.
        "question": prompt              # User query.
    }
    response = agenthelper.lambda_handler(event, None)  # Calls a custom function to handle the query.

    try:
        if response and 'body' in response and response['body']:  # Check if the response contains a body.
            response_data = json.loads(response['body'])          # Parse the body as JSON.
            print("TRACE & RESPONSE DATA ->  ", response_data)    # Debugging output to the console.
        else:
            print("Invalid or empty response received")           # Handle empty or invalid responses.
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)  # Handle JSON parsing errors.
        response_data = None

    try:
        # Format the response and extract trace data
        all_data = format_response(response_data['response'])
        the_response = response_data['trace_data']
    except:
        all_data = "..."  # Fallback data in case of an error.
        the_response = "Apologies, but an error occurred. Please rerun the application"

    # Update the sidebar and session state with the response
    st.sidebar.text_area("", value=all_data, height=300)
    st.session_state['history'].append({"question": prompt, "answer": the_response})
    st.session_state['trace_data'] = the_response

# Handling session end
if end_session_button:  # If the end session button is clicked:
    st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using AnyCompany Support Agent!"})
    event = {
        "sessionId": "MYSESSION",
        "question": "placeholder to end session",
        "endSession": True  # Signal to end the session.
    }
    agenthelper.lambda_handler(event, None)  # Call to handle session end.
    st.session_state['history'].clear()      # Clear the session history.

# Displaying conversation history
st.write("## Conversation History")  # Header for the conversation history section.

# Loading images and applying circular cropping
human_image = Image.open('/home/ubuntu/app/streamlit_app/human_face.jpg')
robot_image = Image.open('/home/ubuntu/app/streamlit_app/robot_face.png')
circular_human_image = crop_to_circle(human_image)
circular_robot_image = crop_to_circle(robot_image)

# Display the conversation history in reverse order
for index, chat in enumerate(reversed(st.session_state['history'])):
    # Question display with image
    col1_q, col2_q = st.columns([2, 10])
    with col1_q:
        st.image(circular_human_image, width=125)  # Display human icon.
    with col2_q:
        st.text_area("Q:", value=chat["question"], height=68, key=f"question_{index}", disabled=True)

    # Answer display with image
    col1_a, col2_a = st.columns([2, 10])
    if isinstance(chat["answer"], pd.DataFrame):
        with col1_a:
            st.image(circular_robot_image, width=100)  # Display robot icon for tabular data.
        with col2_a:
            st.dataframe(chat["answer"], key=f"answer_df_{index}")  # Show DataFrame.
    else:
        with col1_a:
            st.image(circular_robot_image, width=150)  # Display robot icon for text.
        with col2_a:
            st.text_area("A:", value=chat["answer"], height=500, key=f"answer_{index}")

# Example prompts section
st.write("## Test URL Webscrape")  # Header for test prompts.

# Example knowledge base prompts
knowledge_base_prompts = [
    {"Prompt": "Webscrape this url and tell me Jurassic Jade recipe 'https://www.rossandhisjpegs.com/fujifilm-recipes'"},
    {"Prompt": "Webscrape this url and tell me about aerochrome recipe 'https://fujixweekly.com/2024/11/'"}
]

# Display example prompts in a table format
st.table(knowledge_base_prompts)
