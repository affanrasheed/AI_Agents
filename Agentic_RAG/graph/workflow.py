import logging
from typing import Dict, Any, List, Optional
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from nodes.agent_node import agent
from nodes.grade_node import grade_documents
from nodes.rewrite_node import rewrite
from nodes.generate_node import generate
from core.state import AgentState

logger = logging.getLogger(__name__)

class RAGWorkflow:
    """
    Workflow for the RAG agent system.
    
    This class encapsulates the LangGraph workflow that implements the agentic
    RAG pipeline with document retrieval, relevance grading, query rewriting,
    and answer generation.
    """
    
    def __init__(self, tools: Optional[List] = None):
        """
        Initialize the RAG workflow.
        
        Args:
            tools: List of tools to use in the workflow (e.g., retriever tools)
        """
        self.tools = tools or []
        self.graph = None
        
    def build_graph(self):
        """
        Build the workflow graph with all nodes and edges.
        
        Returns:
            Self for method chaining
        """
        logger.info("Building RAG workflow graph")
        
        # Define a new graph with the AgentState type
        workflow = StateGraph(AgentState)
        
        # Set up retrieval tools
        retriever_tools = self.tools
        retrieve = ToolNode(retriever_tools)
        
        # Define the nodes
        workflow.add_node("agent", agent)           # Agent decides whether to use tools or answer directly
        workflow.add_node("retrieve", retrieve)     # Document retrieval
        workflow.add_node("rewrite", rewrite)       # Query reformulation
        workflow.add_node("generate", generate)     # Answer generation
        
        # Set up graph edges
        
        # Start with agent node
        workflow.add_edge(START, "agent")
        
        # Decide whether to retrieve or end
        workflow.add_conditional_edges(
            "agent",
            # Use built-in tools_condition to evaluate agent's decision
            tools_condition,
            {
                # If agent decides to use tools, go to retrieve node
                "tools": "retrieve",
                # Otherwise, end the workflow
                END: END,
            },
        )
        
        # After retrieval, decide if documents are relevant
        workflow.add_conditional_edges(
            "retrieve",
            # Use grade_documents function to evaluate document relevance
            grade_documents,
            {
                # If documents are relevant, generate an answer
                "generate": "generate",
                # If documents aren't relevant, rewrite the query and try again
                "rewrite": "rewrite"
            }
        )
        
        # Connect generate node to end of workflow
        workflow.add_edge("generate", END)
        
        # Connect rewrite node back to agent to restart the process with improved query
        workflow.add_edge("rewrite", "agent")
        
        # Compile the graph
        self.graph = workflow.compile()
        logger.info("Workflow graph compiled successfully")
        
        return self
        
    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the workflow with the given input.
        
        Args:
            input_dict: Dictionary containing input messages
            
        Returns:
            Output from the workflow
        """
        if self.graph is None:
            logger.error("Graph not built. Call build_graph() first.")
            raise ValueError("Graph not built. Call build_graph() first.")
            
        logger.info("Invoking RAG workflow")
        
        # Add tools to the input
        enriched_input = input_dict.copy()
        if "tools" not in enriched_input or not enriched_input["tools"]:
            enriched_input["tools"] = self.tools
        
        return self.graph.invoke(enriched_input)
    
    def stream(self, input_dict: Dict[str, Any]):
        """
        Stream the workflow execution with the given input.
        
        This method yields intermediate results from each step of the workflow,
        allowing for real-time monitoring and debugging.
        
        Args:
            input_dict: Dictionary containing input messages
            
        Returns:
            Generator yielding outputs from each step of the workflow
        """
        if self.graph is None:
            logger.error("Graph not built. Call build_graph() first.")
            raise ValueError("Graph not built. Call build_graph() first.")
            
        logger.info("Streaming RAG workflow")
        
        # Add tools to the input
        enriched_input = input_dict.copy()
        enriched_input["tools"] = self.tools
        
        yield from self.graph.stream(enriched_input)
    
    def get_graph_visualization(self) -> Optional[str]:
        """
        Generate a visualization of the workflow graph.
        
        Returns:
            String representation of the graph in DOT format if available
        """
        try:
            if self.graph is None:
                logger.warning("Cannot visualize graph: not built yet")
                return None
                
            # Get DOT representation (if available)
            return self.graph.get_graph().draw_graphviz()
        except Exception as e:
            logger.error(f"Error generating graph visualization: {e}")
            return None