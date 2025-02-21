import streamlit as st
from openai import OpenAI
import requests

client = OpenAI()

st.set_page_config(layout="wide")

# Header
title = "myfitnessagent"
logo_path = "../logo.png"

if "event_response" not in st.session_state:
    st.session_state.event_response = ""

col1, col2 = st.columns([1, 10])

with col1:
    st.image(logo_path, width=100)

# Display the title in the second column
with col2:
    st.title(title)



if (st.session_state.get("password_correct") == None) or (st.session_state.get("password_correct") == False):
    st.write("Please login first.")
    st.stop()

# Set up the main app page
st.subheader("Let me help you find a patent case!")
# st.write("For example, I can help you find a 5k running event in New York City in August")

with st.form(key='event_form'):
    # event_type = st.text_input("Type of event")
    # location = st.text_input("Location")
    
    case_status = st.text_input("Status of the case")
    time_frame = st.text_input("Year")
    author_country = st.text_input("Author's country code")
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    payload = {
            "case_status": case_status,
            "author_country": author_country,
            "time_frame": time_frame
        }
    
    with st.spinner(f'Looking into cases with {case_status} status from {author_country} in {time_frame}...'):
        response = requests.post("http://localhost:8000/event", json=payload).json()
        st.session_state.event_response = response["response"]
    
# display output
st.write(st.session_state.event_response)
    