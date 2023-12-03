import pickle
from docx import Document
import streamlit as st
import streamlit_authenticator as stauth
from dependencies import sign_up, fetch_users
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as palm
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from htmlTemplates import css,bot_template,user_template
from dotenv import load_dotenv
load_dotenv()

#This will generate text from the pdfs uploaded and return the text
def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        file_name = pdf.name
        text+= "The file name is %s\n"%file_name
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text

#This will take the text, create the chunks and return those chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    chunks = text_splitter.split_text(text)
    return chunks

#This will take GooglePalmEmbeddings, and makes a local vector_store using FAISS
def get_vector_store(text_chunks):
    embeddings = GooglePalmEmbeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def read_previous_text(raw_text):
    readFile = open(data_file, 'rb')
    previous_txt = pickle.load(readFile)
    readFile.close()
    return previous_txt

def write_text_data_file(previous_text):
    writeFile = open(data_file, 'wb')
    pickle.dump(previous_text, writeFile)
    writeFile.close()

def get_conversational_chain(vector_store):
    llm=GooglePalm()
    memory = ConversationBufferMemory(memory_key = "chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vector_store.as_retriever(), memory=memory)
    return conversation_chain

def submit():
    st.session_state.user_question = st.session_state.widget
    st.session_state.widget = ""

def user_input(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chatHistory = response['chat_history']
    chat_history_length = len(st.session_state.chatHistory)

    # Iterate over chat history in reverse order
    for i in range(chat_history_length - 2, -1, -2):
        user_message = st.session_state.chatHistory[i]
        bot_message = st.session_state.chatHistory[i + 1]
        st.write(user_template.replace("{{MSG}}", user_message.content), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", bot_message.content), unsafe_allow_html=True)


def main():
    
    st.set_page_config("Chat with Multiple PDFs")

    st.write(css, unsafe_allow_html=True)

    st.header("Chat with Multiple PDF 💬")
    st.text_input("Ask a Question from the PDF Files", key="widget", on_change=submit)
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    user_question = st.session_state.user_question
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chatHistory" not in st.session_state:
        st.session_state.chatHistory = None
    if user_question:
        user_input(user_question)
    with st.sidebar:
        st.title("Settings")
        st.subheader("Upload your Documents")
        previous_data = st.checkbox("Previous text")
        if(previous_data):
            if st.button("Process"):
                with st.spinner("Processing"):
                    previous_txt = read_previous_text("")
                    print(previous_txt)
                    previous_txt = "\nThis is the previous text\n" + previous_txt
                    write_text_data_file(previous_txt)
                    text_chunks = get_text_chunks(previous_txt)
                    vector_store = get_vector_store(text_chunks)
                    st.session_state.conversation = get_conversational_chain(vector_store)
                    st.success("Done")
        else:
            pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Process Button", accept_multiple_files=True)
            if st.button("Process"):
                with st.spinner("Processing"):
                    raw_text = get_pdf_text(pdf_docs)
                    previous_txt = read_previous_text(raw_text)
                    previous_txt = ""
                    previous_txt = raw_text + "\nThis is the previous text\n" + previous_txt
                    write_text_data_file(previous_txt)
                    text_chunks = get_text_chunks(previous_txt)
                    vector_store = get_vector_store(text_chunks)
                    st.session_state.conversation = get_conversational_chain(vector_store)
                    st.success("Done")



if __name__ == "__main__":
    data_file = "data.obj"
    main()
