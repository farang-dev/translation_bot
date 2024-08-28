import streamlit as st
import docx
import PyPDF2
import io
from openai import OpenAI

# Set page config
st.set_page_config(page_title="Translation Bot", layout="wide")

# Sidebar for settings
st.sidebar.title("Translation Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
translation_style = st.sidebar.selectbox("Translation Style", ["Formal", "Informal", "Creative", "Literal"])
tone = st.sidebar.selectbox("Tone", ["Neutral", "Friendly", "Professional", "Casual"])
target_language = st.sidebar.selectbox("Target Language", ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Italian"])

# Main chat interface
st.title("Translation Bot")

# Initialize chat history and reference document
if "messages" not in st.session_state:
    st.session_state.messages = []
if "reference_document" not in st.session_state:
    st.session_state.reference_document = ""

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Document upload for reference
uploaded_file = st.file_uploader("Upload a reference document", type=["txt", "docx", "pdf"])
if uploaded_file is not None:
    try:
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()

        st.session_state.reference_document = content
        st.success("Reference document uploaded successfully!")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")

# Input for new message
if prompt := st.chat_input("Enter text to translate"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        client = OpenAI(api_key=api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call OpenAI API for translation
        try:
            messages = [
                {"role": "system", "content": f"You are a translator. Translate the following text into {target_language} in a {translation_style} style with a {tone} tone. Use the reference document provided to learn the tone and word choice."},
                {"role": "user", "content": f"Reference document:\n{st.session_state.reference_document}\n\nText to translate:\n{prompt}"}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            translation = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": translation})
            with st.chat_message("assistant"):
                st.markdown(translation)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Note: The document translation feature has been removed as it's no longer needed.
