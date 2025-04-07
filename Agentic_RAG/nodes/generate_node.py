import logging
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from core.config import GENERATOR_MODEL

logger = logging.getLogger(__name__)

def generate(state):
    """
    Generate an answer based on the retrieved documents and question.

    Args:
        state (messages): The current state containing messages

    Returns:
        dict: The updated state with generated answer
    """
    logger.info("Generating answer from retrieved documents")
    
    # Get messages and extract question and documents
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]
    docs = last_message.content
    
    # Load RAG prompt from hub
    prompt = hub.pull("rlm/rag-prompt")
    
    # Create ChatOpenAI model
    llm = ChatOpenAI(
        model_name=GENERATOR_MODEL, 
        temperature=0, 
        streaming=True
    )
    
    # Document formatting function for the prompt
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create the RAG chain
    rag_chain = prompt | llm | StrOutputParser()
    
    # Invoke chain
    response = rag_chain.invoke({"context": docs, "question": question})
    
    logger.info(f"Generated answer: {response[:100]}...")
    
    # Return response
    return {"messages": [response]}