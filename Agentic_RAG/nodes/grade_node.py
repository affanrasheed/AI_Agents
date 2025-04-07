import logging
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from core.config import GRADER_MODEL

logger = logging.getLogger(__name__)

class DocumentRelevanceGrade(BaseModel):
    """Binary score for relevance check."""
    binary_score: str = Field(description="Relevance score 'yes' or 'no'")

def grade_documents(state) -> Literal["generate", "rewrite"]:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (messages): The current state containing messages

    Returns:
        str: A decision for whether the documents are relevant or not
    """
    logger.info("Grading document relevance")
    
    # LLM
    model = ChatOpenAI(temperature=0, model=GRADER_MODEL, streaming=True)
    
    # LLM with structured output validation
    llm_with_tool = model.with_structured_output(DocumentRelevanceGrade)
    
    # Prompt for document relevance grading
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
        input_variables=["context", "question"],
    )
    
    # Create chain
    chain = prompt | llm_with_tool
    
    # Get messages and extract question and context
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]
    docs = last_message.content
    
    # Invoke chain
    scored_result = chain.invoke({"question": question, "context": docs})
    score = scored_result.binary_score
    
    # Log decision
    if score == "yes":
        logger.info("Document graded as relevant")
        return "generate"
    else:
        logger.info("Document graded as not relevant")
        return "rewrite"