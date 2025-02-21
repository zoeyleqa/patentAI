import os
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent

from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough

from transformers import AutoTokenizer, AutoModelForCausalLM

from dotenv import load_dotenv

# load_dotenv()
class RagAgent:

    def __init__(self, problem: str):
        load_dotenv()

        # load docs
        file_path = "../pdfs"
        docs = []
        for file in os.listdir(file_path):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(file_path, file)
                loader = PyPDFLoader(pdf_path)
                docs.extend(loader.load())

        # split and index
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=0)

        chunked_docs = splitter.split_documents(docs)

        self.vector_store = FAISS.from_documents(chunked_docs, HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5"))

        self.retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})


        # LLM model name
        model_name ="TinyLlama/TinyLlama-1.1B-Chat-v1.0"

        save_directory = "../notebooks/model_directory"

        # Get the list of files and directories in 'save_directory'
        directory_contents = os.listdir(save_directory)

        # Check if the directory is empty
        if not directory_contents:
            print(f"The directory {save_directory} is empty.")
            model = AutoModelForCausalLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            tokenizer.save_pretrained(save_directory)
            model.save_pretrained(save_directory)

        else:
            print(f"The directory {save_directory} contains {len(directory_contents)} items.")
            model = AutoModelForCausalLM.from_pretrained(save_directory)
            tokenizer = AutoTokenizer.from_pretrained(save_directory)

        # build LLM pipeline
        text_generation_pipeline = pipeline(
            model=model,
            tokenizer=tokenizer,
            task="text-generation",
            temperature=0.2,
            do_sample=True,
            repetition_penalty=1.1,
            return_full_text=True,
            max_new_tokens=400,
        )

        llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

        # RAG Prompt template
        prompt_template = """
        <|system|>
        Answer the question based on your knowledge. Use the following context to help:

        {context}

        </s>
        <|user|>
        {question}
        </s>
        <|assistant|>

        """

        # RAG chain
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template,
        )

        self.llm_chain = prompt | llm | StrOutputParser()


    # def learn_new_case(applId):
        # download
        # load
