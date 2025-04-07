import os
import logging
from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage
import threading

# Import components
from core.config import setup_environment, DEFAULT_URLS
from core.state import UIState
from components.document_loader import DocumentLoader
from components.embeddings import EmbeddingManager
from components.vectorstore import VectorStoreManager
from components.retriever import RetrieverToolFactory
from graph.workflow import RAGWorkflow

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup environment variables
setup_environment()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize global state
ui_state = UIState()
document_loader = None
vector_store_manager = None
retriever_factory = None
workflow = None
workflow_lock = threading.Lock()

def initialize_pipeline(urls=None):
    """Initialize the RAG pipeline with the given URLs."""
    global document_loader, vector_store_manager, retriever_factory, workflow
    
    # Use default URLs if none provided
    urls = urls or DEFAULT_URLS
    
    try:
        # Initialize document loader
        document_loader = DocumentLoader()
        
        # Load and split documents
        documents = document_loader.load_from_urls(urls)
        
        # Initialize embedding manager
        embedding_manager = EmbeddingManager()
        
        # Initialize vector store
        vector_store_manager = VectorStoreManager(embedding_manager=embedding_manager)
        vector_store_manager.create_from_documents(documents)
        
        # Initialize retriever
        retriever_factory = RetrieverToolFactory(vector_store_manager=vector_store_manager)
        retriever_tool = retriever_factory.create_retriever_tool()
        
        # Initialize workflow
        workflow = RAGWorkflow(tools=[retriever_tool])
        workflow.build_graph()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing pipeline: {e}")
        return False

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize():
    """Initialize the RAG pipeline."""
    data = request.json
    urls = data.get('urls', DEFAULT_URLS)
    
    success = initialize_pipeline(urls)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Pipeline initialized successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to initialize pipeline'}), 500

@app.route('/query', methods=['POST'])
def query():
    """Process a query using the RAG pipeline."""
    global workflow, ui_state
    
    data = request.json
    query_text = data.get('query', '')
    
    if not query_text:
        return jsonify({'status': 'error', 'message': 'Query text is required'}), 400
        
    if not workflow:
        initialize_success = initialize_pipeline()
        if not initialize_success:
            return jsonify({'status': 'error', 'message': 'Failed to initialize pipeline'}), 500
    
    # Add query to UI state
    ui_state.add_message('user', query_text)
    
    try:
        # Set processing state
        ui_state.set_processing(True)
        
        # Create input for the workflow
        workflow_input = {
                            "messages": [
                                HumanMessage(content=query_text)
                            ],
                            "tools": retriever_factory.tools if retriever_factory else []
                        }
        
        # Process results
        results = []
        
        # Use lock to prevent concurrent workflow executions
        with workflow_lock:
            # Stream workflow execution
            for output in workflow.stream(workflow_input):
                for key, value in output.items():
                    step_result = {
                        'step': key,
                        'content': str(value)
                    }
                    results.append(step_result)
                    ui_state.add_debug_info(key, str(value))
                    
                    # Update current step
                    ui_state.set_current_step(key)
        
        # Get final answer from results
        final_answer = "No answer generated"
        for result in reversed(results):
            if result['step'] == 'generate':
                final_answer = result['content']
                break
        
        # Add response to UI state
        ui_state.add_message('assistant', final_answer)
        
        # Reset processing state
        ui_state.set_processing(False)
        
        return jsonify({
            'status': 'success',
            'answer': final_answer,
            'steps': results,
            'history': ui_state.history
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        ui_state.set_processing(False)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get the conversation history."""
    global ui_state
    return jsonify({'history': ui_state.history})

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear the conversation history."""
    global ui_state
    ui_state.clear_history()
    return jsonify({'status': 'success', 'message': 'History cleared'})

@app.route('/status', methods=['GET'])
def get_status():
    """Get the status of the pipeline."""
    global workflow, ui_state
    
    status = {
        'initialized': workflow is not None,
        'processing': ui_state.processing,
        'current_step': ui_state.current_step
    }
    
    return jsonify(status)

if __name__ == '__main__':
    # Initialize the pipeline on startup
    initialize_pipeline()
    app.run(debug=True)