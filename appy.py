import PyPDF2
import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key="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",
)

st.title("PDF Content Analyzer")

# Add a sidebar button for history
show_history = st.sidebar.button("Show History")

# Session state for storing chat history and continuing the chat
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'continue_chat' not in st.session_state:
    st.session_state['continue_chat'] = True

# Upload PDF file
uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

# PDF Content Analysis
if uploaded_pdf is not None:
    # Extract text from the PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
    pdf_content = ""
    
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            pdf_content += text + "\n\n"

    # Analyze PDF content with Groq Cloud when button is pressed
    if st.button("Analyze PDF Content"):
        # Send the PDF content to Groq Cloud for analysis
        full_prompt = f"Document content:\n\n{pdf_content}\n\nAnalyze and summarize the document."
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama3-8b-8192",
        )
        analysis_result = response.choices[0].message.content
        
        # Display the analysis result
        st.subheader("Analysis Result:")
        st.markdown(f"""<div style='background-color: #e8f0fe; padding: 10px; border-radius: 5px;'>
                      <p style='white-space: pre-wrap;'>{analysis_result}</p>
                      </div>""", unsafe_allow_html=True)

    # Input for asking questions after analysis
    if st.session_state['continue_chat']:
        user_question = st.text_input("Ask a question about the PDF content:")

        if user_question:
            # Combine the PDF content with the user question
            full_prompt = f"Document content:\n\n{pdf_content}\n\nUser question: {user_question}\nAnswer the question based on the document content."
            
            # Send the question to Groq Cloud and get the answer
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="llama3-8b-8192",
            )
            answer = response.choices[0].message.content
            
            # Store question and answer in chat history
            st.session_state['chat_history'].append({'question': user_question, 'answer': answer})

            # Display the answer
            st.subheader("Answer to Your Question:")
            st.markdown(f"""<div style='background-color: #e8f0fe; padding: 10px; border-radius: 5px;'>
                                  <p style='white-space: pre-wrap;'>{answer}</p>
                                  </div>""", unsafe_allow_html=True)

            # Ask the user if they want to continue or exit
            continue_chat = st.radio("Do you want to continue chatting?", ("Continue", "Exit"))

            if continue_chat == "Exit":
                st.session_state['continue_chat'] = False
                st.write("Chat ended. Thank you!")

            elif continue_chat == "Continue":
                st.session_state['continue_chat'] = True  # Allow new questions

    # Display history if button is clicked
    if show_history:
        st.subheader("Previous Chat History:")
        for chat in st.session_state['chat_history']:
            st.write(f"Q: {chat['question']}")
            st.write(f"A: {chat['answer']}")
