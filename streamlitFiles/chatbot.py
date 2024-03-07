import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv() 
genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro") 

def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input= ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def main():
    st.title("Chat BOT")
    chat_container = st.container()


    if "send_input" not in st.session_state:
        st.session_state.send_input = False
        st.session_state.user_question= ""
        st.session_state.new_session_key=None


   
    user_input = st.text_input("Type your message here", key= "user_input",on_change=set_send_input)
    send_button = st.button("Send",key= "send_button")

    if send_button or st.session_state.send_input:
        if st.session_state.user_question!= "":
            response= get_gemini_response(st.session_state.user_question)
            

            with chat_container:
                st.chat_message("user").write(st.session_state.user_question)
                st.chat_message("ai").write(response)
                st.session_state.user_question= ""



if __name__ == "__main__":
    main()