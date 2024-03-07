from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from flask import send_file,url_for
from flask import send_from_directory
import requests
import os

load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', image_url='')

@app.route('/send-text', methods=['POST'])
def send_text():
    data = request.get_json()
    user_question = data['user_question']
    response = get_gemini_response(user_question)
    return jsonify({'response': response})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    user_question = data['textInput']
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    # Make a request to the API to generate the image
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payloads = {
        'inputs': user_question,
    }
    response = requests.post(API_URL, json=payloads, headers=headers)

    if response.status_code == 200:
        with open('static\image.jpg', 'wb') as file:
            file.write(response.content)
        # Return the URL of the generated image
        return jsonify({'image_url': 'static\image.jpg'})
    else:
        return jsonify({'error': 'Failed to generate image'})


UPLOAD_FOLDER = 'static/audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    message = data['message']

    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payloads = {
        "inputs": message
    }
    response = requests.post(API_URL, headers=headers, json=payloads)
    
    if response.status_code == 200:
        return response.content, 200, {'Content-Type': 'audio/flac'}
    else:
        return jsonify({'error': 'Failed to generate audio'})


@app.route('/audio/<path:filename>')
def audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/save-audio', methods=['POST'])
def audio2text():
    audio_file = request.files['audio']
    audio_file.save('path/to/save/recorded_audio.wav')
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    with open('path/to/save/recorded_audio.wav', 'rb') as f:
        audio_data = f.read()
    response = requests.post(API_URL, headers=headers, data=audio_data)
    result = response.json()
    # Process the result to get the generated text
    generated_text = result['generated_text']
    
    # Assuming get_gemini_pro_response is a function to generate a response based on text
    gemini_response = get_gemini_pro_response(generated_text)
    
    # Return the gemini response as JSON
    return jsonify({'response': gemini_response})


def get_gemini_pro_response(question):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(question)
    return response.text

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = file.filename
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    return jsonify({'file_path': file_path})

@app.route('/generate-text', methods=['POST'])
def generate_text():
    file_path = request.form.get('file_path')
    if not file_path:
        return jsonify({'error': 'No file path provided'})

    # Choose the appropriate API_URL based on the file type
    if file_path.endswith('.jpg') or file_path.endswith('.png'):
        API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    elif file_path.endswith('.pdf'):
        # Choose appropriate API for PDF processing
        pass
    else:
        return jsonify({'error': 'Unsupported file type'})

    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    with open(file_path, "rb") as f:
        data = f.read()

    response = requests.post(API_URL, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result and isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            text = result[0]['generated_text']
            return jsonify({'text': text})
        else:
            return jsonify({'error': 'No generated text found in the response'})
    else:
        return jsonify({'error': f'Error: {response.status_code}'})
    

def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_link = data.get('video_link')
    prompt="""You are Yotube video summarizer. You will be taking the transcript text
    and summarizing the entire video and providing the important summary in points
    within 250 words. Please provide the summary of the text given here:  """
    transcript_text=extract_transcript_details(video_link)
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text




if __name__ == '__main__':
    app.run(debug=True)

