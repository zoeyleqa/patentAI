from typing import Dict
from fastapi import FastAPI

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
from unstructured.staging.base import elements_from_json
from langchain_core.documents import Document
from huggingface_hub.hf_api import HfFolder

import os
import sqlite3
import re
import torch
from dotenv import load_dotenv
from prompts import patent_agent_prompt

load_dotenv("../.env")


###########################
### ReAct Search Agent ####
###########################

# Create the agent with memory and search tool
memory = sqlite3.connect(":memory:")
model = ChatOpenAI(model='gpt-4o')
search = TavilySearchResults(max_results=2)
tools = [search]
agent_executor = create_react_agent(model, tools, checkpointer=memory)

###########################
###   Patent Agent  ####
###########################

# use the ingest functionality to partition PDF files in a local directory.
directory_with_pdfs="./pdfs"
directory_with_results="./processed_pdfs"

if len(os.listdir(directory_with_results)) == 0:
    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=LocalIndexerConfig(input_path=directory_with_pdfs),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=os.getenv("UNSTRUCTED_API_KEY"),
            partition_endpoint=os.getenv("UNSTRUCTURED_API_URL"),
            strategy="hi_res",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_concurrency_level": 15,
                },
            ),
        uploader_config=LocalUploaderConfig(output_dir=directory_with_results)
    ).run()

# Load document elements from json outputs, create LangChain documents from document chunks 
# and their metadata, and ingest those documents into the FAISS vectorstore.
def load_processed_files(directory_path):
    elements = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            try:
                elements.extend(elements_from_json(filename=file_path))
            except IOError:
                print(f"Error: Could not read file {filename}.")

    return elements

elements = load_processed_files(directory_with_results)

documents = []
for element in elements:
    metadata = element.metadata.to_dict()
    documents.append(Document(page_content=element.text, metadata=metadata))

db = FAISS.from_documents(documents, HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5"))
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Now, let's finally set up llama 3 to use for text generation in the RAG system.
# This is a gated model, which means you first need to go to the model's page, log in, 
# review terms and conditions, and request access to it. To use the model in the notebook, 
# you need to log in with your Hugging Face token (get it in your profile's settings).
HfFolder.save_token(os.getenv("HUGGINGFACE_TOKEN"))

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
# model_name ="TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True, 
#     bnb_4bit_use_double_quant=True, 
#     bnb_4bit_quant_type="nf4", 
#     bnb_4bit_compute_dtype=torch.bfloat16
# )

save_directory = "../notebooks/model_directory"

# Get the list of files and directories in 'save_directory'
directory_contents = os.listdir(save_directory)

# Check if the directory is empty
if not directory_contents:
    print(f"The directory {save_directory} is empty.")
    # model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)

else:
    print(f"The directory {save_directory} contains {len(directory_contents)} items.")
    model = AutoModelForCausalLM.from_pretrained(save_directory)
    tokenizer = AutoTokenizer.from_pretrained(save_directory)

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

text_generation_pipeline = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
    temperature=0.2,
    do_sample=True,
    repetition_penalty=1.1,
    return_full_text=False,
    max_new_tokens=200,
    eos_token_id=terminators,
)

llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=patent_agent_prompt,
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# load docs
# file_path = "./pdfs"
# docs = []
# for file in os.listdir(file_path):
#     if file.endswith('.pdf'):
#         pdf_path = os.path.join(file_path, file)
#         loader = PyPDFLoader(pdf_path)
#         docs.extend(loader.load())

# split and index
# splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=0)

# chunked_docs = splitter.split_documents(docs)

# db = FAISS.from_documents(chunked_docs, HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5"))

# retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})


###########################
###    App Endpoint    ####
###########################

app = FastAPI()

@app.post("/patent")
def patent_research(data: Dict):
    question = data['question']
    response = rag_chain.invoke(question)
    print(response)
    
    # Regular expression to match everything after <|assistant|>
    # pattern = r"(?<=<\|assistant\|>)[\s\S]*$"
    
    # # Perform the regex search
    # match = re.search(pattern, response, re.DOTALL)

    # Check if a match is found and print the result
    if response:
        result = response
        # print(result)
    else:
        result = "Try again"
        
    return {"response": result}
# 16948574
@app.post("/event")
def generate_events(data: Dict):
    print(data)
    case_status = data["case_status"]
    author_country = data["author_country"]
    time_frame = data["time_frame"]
    user_input = f"Find me cases with {case_status} status from {author_country} in {time_frame}. Return back specific events."

    # Set memory for a specific user
    config = {"configurable": {"thread_id": "rc45"}}

    response = agent_executor.invoke({"messages": [("user", user_input)]}, config)

    response = response["messages"][-1].content
    return {"response": response}