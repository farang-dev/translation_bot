import streamlit as st
import openai
import docx
import PyPDF2
import io

# Set page config
st.set_page_config(page_title="Translation Bot", layout="wide")

# Sidebar for settings
st.sidebar.title("Translation Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
translation_style = st.sidebar.selectbox("Translation Style", ["Formal", "Informal", "Creative", "Literal"])
tone = st.sidebar.selectbox("Tone", ["Neutral", "Friendly", "Professional", "Casual"])

# Main chat interface
st.title("Translation Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
try:
    import docx
except ImportError:
    st.error("The 'docx' module is not installed. Please install it using 'pip install python-docx'.")
    st.stop()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for new message
if prompt := st.chat_input("Enter text to translate"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        client = openai.OpenAI(api_key=api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call OpenAI API for translation
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a translator. Translate the following text in a {translation_style} style with a {tone} tone."},
                    {"role": "user", "content": prompt}
                ]
            )

            translation = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": translation})
            with st.chat_message("assistant"):
                st.markdown(translation)
        except openai.OpenAIError as e:
            st.error(f"An error occurred: {str(e)}")
# Document upload
uploaded_file = st.file_uploader("Upload a document", type=["txt", "docx", "pdf"])
if uploaded_file is not None:
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
    # Check if PyPDF2 is installed
    try:
        import PyPDF2
    except ImportError:
        st.error("The 'PyPDF2' module is not installed. Please install it using 'pip install PyPDF2'.")
        st.stop()

    st.text_area("Document Content", content, height=300)

    # Allow user to modify the content before translation
    modified_content = st.text_area("Modify content (if needed)", content, height=300)

    if st.button("Translate Document"):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        else:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a translator. Translate the following document in a {translation_style} style with a {tone} tone."},
                    {"role": "user", "content": modified_content}
                ]
            )
            translation = response.choices[0].message.content
            st.text_area("Translated Document", translation, height=300)

# Note: The Google Drive integration has been removed as per the followup instructions.
