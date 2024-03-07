from dotenv import find_dotenv, load_dotenv
import streamlit as st
import requests
import os

# Load environment variables
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")


def generate_img(text):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    image_width = 500
    image_height = 500
    payloads = {
        "inputs":text,
        'image_width': image_width,
        'image_height': image_height
    }

    response = requests.post(API_URL, headers=headers, json=payloads)
    return response.content

# Streamlit app
def main():
    st.title("Image Generation from Text")
    st.write("Enter a description to generate an image.")

    text_input = st.text_input("Enter text description")

    if st.button("Generate Image"):
        image_data = generate_img(text_input)
        st.image(image_data, caption='Generated Image', use_column_width=True)

if __name__ == "__main__":
    main()
