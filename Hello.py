import streamlit as st
import os
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
from PIL import Image
import streamlit as st


if not os.path.exists('tempDir'):
    os.makedirs('tempDir')

# Make sure to replace 'your_openai_api_key' with your actual OpenAI API key
os.environ['OPENAI_API_KEY'] = st.secrets["apikey"]

def text_to_notes(text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in taking down notes as bullet points and summarizing big conversations. you make sure no detail is left out. Just share the summarization. Do nor share any additional comments."
            },
            {
                "role": "user",
                "content": f"Here is my conversation: {text}"
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    notes = response.choices[0].message.content
    return notes

def transcribe(location):
    client = OpenAI()
    
    with open(location, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text

def save_uploadedfile(uploaded_file):
    with open(os.path.join('tempDir', uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success(f"Saved File: {uploaded_file.name} to tempDir")

image = Image.open("lyzr-logo.png")
st.image(image, caption="", width=150)

st.title("Transcribe Audio with Whisper")
st.write('Note: The recording will stop as soon as your pause/stop speaking. So continue to speak without a break to get the full transcript.')
# Record audio
audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    # Save the recorded audio for transcription
    with open('tempDir/output.wav', 'wb') as f:
        f.write(audio_bytes)
    transcript = transcribe('tempDir/output.wav')
    st.write(transcript)
    if transcript:
        ainotes = text_to_notes(transcript)
        st.write(ainotes)

# Or upload audio file
st.subheader('Upload any audio file (.wav format only) and get the transcript', divider=True)
uploaded_file = st.file_uploader("Upload Files", type=['wav'])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    save_uploadedfile(uploaded_file)
    audio_file = open(os.path.join('tempDir', uploaded_file.name), "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/wav')
    transcript = transcribe(os.path.join('tempDir', uploaded_file.name))
    st.write(transcript)
    if transcript:
        ainotes = text_to_notes(transcript)
        st.write(ainotes)

        