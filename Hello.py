import os
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
from PIL import Image
import streamlit as st

# Create a temporary directory if it doesn't exist
if not os.path.exists('tempDir'):
    os.makedirs('tempDir')

# Setup your OpenAI API key
os.environ['OPENAI_API_KEY'] = st.secrets["apikey"]

# Function definitions (text_to_notes, transcribe, save_uploadedfile, etc.) go here...
def text_to_notes(text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a bank employee tasked with reviewing a recently obtained audio recording of a client's interview. This recording contains essential personal data that needs to be extracted to create a formal profile for the client. Your job is to listen to the recording carefully, transcribe the relevant details, and format this information into a clear and professional document that can be added to the bank’s client records system. The information you need to present includes:\n\n1. **Client’s Full Name:** Ensure that the spelling is accurate as it will be used for all official documents.\n2. **Age:** Verify that the age mentioned matches with any official identification provided.\n3. **Father's Name:** This might be required for additional identity verification purposes.\n4. **Address:** Confirm the complete and current residential address.\n5. **Email ID:** Take down the email address, making sure it is spelled correctly as it will be a primary mode of communication.\n6. **Occupation:** Note down the client's self-stated profession.\n7. **Designation:** If the client mentions their job title, record this as it may relate to the services they require.\n8. **Phone Number:** Include country and area codes to ensure contactability.\n9. **Date of Birth:** This must match with the provided legal documents.\n10. **Origin of Birth:** This could be relevant for citizenship verification or international regulations.\n11. **Primary Inquiry:** Identify the main reason for the client’s visit or call, which could to be open an account, apply for a loan, etc.\n12. **Documents Submitted:** Make a checklist of all the documents the client claims to have submitted during the intake process.\n\nAfter gathering all this information, organize it in the following format:\n\n---\n\n**Client Profile Transcript Presentation**\n\n- **Name:** [Client's Full Name]\n- **Age:** [Client's Age]\n- **Father's Name:** [Father's Full Name]\n- **Address:** [Complete Address]\n- **Email ID:** [Email Address]\n- **Occupation:** [Occupation]\n- **Designation:** [Designation]\n- **Phone Number:** [Full Phone Number]\n- **Date of Birth:** [DOB in format DD/MM/YYYY]\n- **Origin of Birth:** [Country/City of Birth]\n- **Primary Inquiry:** [Summary of Inquiry or Request]\n- **Documents Submitted:**\n  - [Document 1]\n  - [Document 2]\n  - [Document 3]\n  - [Etc.]\n\n---\n\nEnsure this document is legible, thoroughly checked for accurate transcription, and appropriate for bank use. Securely file the document and enter the details into the bank's client records management system as per your institution's protocols. Remember to handle all personal information with confidentiality and in accordance with data protection regulations."
            },
            {
                "role": "user",
                "content": f"Here is my transcript: {text}"
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

# Custom function to style the app
def style_app():
    # You can put your CSS styles here
    st.markdown("""
    <style>
    .app-header { visibility: hidden; }
    .css-18e3th9 { padding-top: 0; padding-bottom: 0; }
    .css-1d391kg { padding-top: 1rem; padding-right: 1rem; padding-bottom: 1rem; padding-left: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# Call the function to apply the styles
style_app()

# Load and display the logo
image = Image.open("lyzr-logo.png")
st.image(image, width=150)

# App title and introduction
st.title("Smart Form Filler Demo")
st.markdown("### Welcome to the Smart Form Filler!")
st.markdown("Upload an audio recording or record your voice directly, and let the AI assist in filling out forms based on the transcript.")

# Instruction for the users
st.markdown("#### 🎤 Record or Upload Audio")
st.caption('Note: The recording will stop as soon as you pause/stop speaking. Please continue to speak without a break to get the full transcript.')

# Start of the main container
with st.container():
    audio_bytes = audio_recorder()
    if audio_bytes:
        # Record audio
        st.audio(audio_bytes, format="audio/wav")
        # Save the recorded audio for transcription
        with open('tempDir/output.wav', 'wb') as f:
            f.write(audio_bytes)
        transcript = transcribe('tempDir/output.wav')
        changes = st.text_area("Transcript", transcript, height=150)
        transcript = changes
        st.markdown("---")
        # st.write(changes)
        # Display AI Notes section title
        st.markdown("#### 📝 AI Notes")
        if transcript:
            ainotes = text_to_notes(transcript)
            st.markdown(ainotes)

# Additional features such as file upload can be added in a similar styled container

# Footer or any additional information
with st.expander("ℹ️ - About this App"):
    st.markdown("""
    This app uses GPT-3 to generate notes from transcribed audio. The audio transcription is powered by OpenAI's Whisper model. For any inquiries or issues, please contact [Support Email]. 
    """)