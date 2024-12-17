import streamlit as st
from PIL import Image
import requests
import base64
import io
import simplejson as json  # Instead of jsonlib

# Your API key
API_KEY = "your api key"

# Google Vision API and Text-to-Speech URLs
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"
TTS_URL = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"

# Set the page layout and custom title with emoji
st.set_page_config(
    page_title="AI-Powered Assistance",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 1rem;
    }
    .description {
        font-size: 1.2rem;
        color: #555555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .button-style {
        display: block;
        margin: 0 auto;
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px;
        font-size: 1rem;
        cursor: pointer;
        border-radius: 5px;
    }
    .button-style:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-title">AI-Powered Assistance for Visually Impaired Individuals</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Enhancing accessibility with scene understanding, text-to-speech, and personalized guidance.</div>', unsafe_allow_html=True)

# File uploader
uploaded_image = st.file_uploader("📤 Upload an Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_image:
    col1, col2 = st.columns(2)

    # Display uploaded image in a column
    with col1:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Convert the image to base64 for API requests
    image = Image.open(uploaded_image)
    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format='PNG')
    image_base64 = base64.b64encode(image_byte_array.getvalue()).decode()

    with col2:
        st.markdown("### Features")
        st.write("Choose one of the options below to process the uploaded image:")

        # Scene Understanding
        if st.button("🔍 Generate Scene Description", key="scene"):
            st.write("Analyzing the image for scene understanding...")
            vision_payload = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "LABEL_DETECTION", "maxResults": 10}],
                    }
                ]
            }

            response = requests.post(VISION_URL, json=vision_payload)

            if response.status_code == 200:
                labels = response.json()["responses"][0].get("labelAnnotations", [])
                if labels:
                    st.success("### Scene Description")
                    st.write(", ".join(label["description"] for label in labels))
                else:
                    st.error("No scene description could be generated.")
            else:
                st.error(f"Vision API Error: {response.text}")

        # Object Detection
        if st.button("🛠 Detect Objects and Obstacles", key="objects"):
            st.write("Analyzing the image for objects and obstacles...")
            vision_payload = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "OBJECT_LOCALIZATION", "maxResults": 10}],
                    }
                ]
            }

            response = requests.post(VISION_URL, json=vision_payload)

            if response.status_code == 200:
                objects = response.json()["responses"][0].get("localizedObjectAnnotations", [])
                if objects:
                    st.success("### Detected Objects and Obstacles")
                    for obj in objects:
                        st.write(f"- **{obj['name']}** (Confidence: {obj['score']:.2f})")
                else:
                    st.error("No objects or obstacles detected.")
            else:
                st.error(f"Vision API Error: {response.text}")

        # Text Extraction and Text-to-Speech
        if st.button("🎙 Convert Text to Speech", key="tts"):
            st.write("Extracting text from the image...")
            text_payload = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "TEXT_DETECTION"}],
                    }
                ]
            }

            text_response = requests.post(VISION_URL, json=text_payload)

            if text_response.status_code == 200:
                annotations = text_response.json()["responses"][0].get("textAnnotations", [])
                if annotations:
                    extracted_text = annotations[0]["description"]
                    st.write("### Extracted Text")
                    st.text(extracted_text)

                    # Convert the extracted text to speech
                    st.write("Converting text to speech...")
                    tts_payload = {
                        "input": {"text": extracted_text},
                        "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
                        "audioConfig": {"audioEncoding": "MP3"},
                    }

                    tts_response = requests.post(TTS_URL, json=tts_payload)
                    if tts_response.status_code == 200:
                        audio_content = tts_response.json().get("audioContent")
                        if audio_content:
                            audio_bytes = base64.b64decode(audio_content)
                            st.audio(audio_bytes, format="audio/mp3")
                        else:
                            st.error("No audio content received from the Text-to-Speech API.")
                    else:
                        st.error(f"Text-to-Speech API Error: {tts_response.text}")
                else:
                    st.error("No text found in the image.")
            else:
                st.error(f"Vision API Error: {text_response.text}")

        # Personalized Guidance
        if st.button("🤖 Provide Personalized Guidance", key="guidance"):
            st.write("Analyzing the image for personalized guidance...")
            text_payload = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "TEXT_DETECTION"}],
                    }
                ]
            }

            text_response = requests.post(VISION_URL, json=text_payload)

            if text_response.status_code == 200:
                annotations = text_response.json()["responses"][0].get("textAnnotations", [])
                if annotations:
                    extracted_text = annotations[0]["description"]
                    st.write("### Recognized Text")
                    st.text(extracted_text)

                    # Provide contextual guidance
                    st.write("### Personalized Guidance")
                    if "expiry" in extracted_text.lower():
                        st.warning("The image contains expiry information. Check the dates carefully.")
                    elif "warning" in extracted_text.lower():
                        st.warning("The image contains a warning label. Exercise caution.")
                    elif "ingredient" in extracted_text.lower():
                        st.info("The image contains ingredient information. Review for dietary preferences.")
                    else:
                        st.info("No specific guidance detected.")
                else:
                    st.error("No text found in the image.")
            else:
                st.error(f"Vision API Error: {text_response.text}")
