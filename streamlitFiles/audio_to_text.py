from dotenv import find_dotenv, load_dotenv
import streamlit as st
import requests
import os
import tempfile

# Load environment variables
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Function to generate text from audio
def generate_text(audio_path):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    response = requests.post(API_URL, headers=headers, data=audio_data)
    result = response.json()
    if result and isinstance(result, dict) and 'text' in result:
        return result['text']
    else:
        return None

# Streamlit app
def main():
    st.title("Text Generation from Audio")
    st.write("Upload an audio file in FLAC format to generate text.")

    uploaded_file = st.file_uploader("Upload FLAC audio file", type="flac")

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        if st.button("Generate Text"):
            text = generate_text(temp_file_path)
            if text:
                st.write("Generated Text:")
                st.write(text)
            else:
                st.write("Text generation failed. Please try again.")

        os.unlink(temp_file_path)  # Delete temporary file after use

    else:
        st.write("Please upload a FLAC audio file.")

if __name__ == "__main__":
    main()
