from dotenv import find_dotenv, load_dotenv
import google.generativeai as genai
import streamlit as st
import requests
import os

load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def img2text(url):
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    with open(url, "rb") as f:
        data = f.read()
    # Send request to the API
    response = requests.post(API_URL, headers=headers, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        # Check if 'generated_text' exists in the response
        if result and isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            text = result[0]['generated_text']
            return text
        else:
            return "No generated text found in the response."
    else:
        return f"Error: {response.status_code}"


# llm
def get_story(scenario):
    prompt_template = """
    You are a story teller;
    You can generate a short story based on a simple narrative, the story should be no more than 30 words;\n\n
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt_template + scenario)
    story = response.text
    print(story)
    return story
    

# text to speech
def text2speech(message):
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payloads = {
        "inputs":message
    }
    response=requests.post(API_URL,headers=headers,json=payloads)
    with open('audio.flac','wb') as file:
        file.write(response.content)

def main():
    st.set_page_config(page_title= "Img 2 audio generator")

    st.header("Turn image into audio story")
    uploaded_file = st.file_uploader("Choose an image..", type= ["jpg","jpeg","png"])

    if uploaded_file is not None:
        print(uploaded_file)
        bytes_data =uploaded_file.getvalue()
        with open(uploaded_file.name,"wb") as file:
            file.write(bytes_data)
        st.image(uploaded_file, caption= "Uploaded Image", use_column_width=True)
        scenario = img2text(uploaded_file.name)
        story = get_story(scenario)
        text2speech(story)

        with st.expander("scenario"):
            st.write(scenario)
        with st.expander("story"):
            st.write(story)

        st.audio("audio.flac")

if __name__ == "__main__":
    main()
