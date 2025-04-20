import streamlit
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from google import genai

# Configuration
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
cwd=os.getcwd()#Current working directory
PDF=os.path.join(cwd,"PDF")#List of pdf files
def llama_simple_reader(path):
    try:
        documents = SimpleDirectoryReader(input_files=[path]).load_data()
        return documents
    except Exception as e:
        print(f"Unable to read: {path}: {e}")
        return []

def chunk_documents(file_name,documents, path, chunk_size, chunk_overlap):
    record_dict = {}
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = parser.get_nodes_from_documents(documents)
    for pos, node in enumerate(nodes):
        ID = f"{file_name}_{pos}"
        record_dict[ID] = node
    return nodes, record_dict

def embed_record_dict(record_dict, embedding_model):
    embeddings = []
    ids = []
    for doc_id, node in record_dict.items():
        text = node.text
        embedding = embedding_model.encode(text, show_progress_bar=False)
        embeddings.append(embedding)
        ids.append(doc_id)
    return embeddings, ids

def index_embeddings(embeddings, ids, record_dict, file_name):
    cwd=os.getcwd()#Current working directory
    index_folder=os.path.join(cwd,"indexed_pdfs")#Folder where files are indexed
    embeddings_array = np.array(embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_array)
    
    # Store all original metadata
    metadata_store = {}
    for i, id_ in enumerate(ids):
        node = record_dict[id_]
        metadata_store[id_] = {
            'text': node.text,
            'metadata': dict(node.metadata),
            'faiss_index': i
        }
    
    # Fix: Write index to file correctly
    save_path=os.path.join(index_folder,f"{file_name}__index.faiss")#Save path
    faiss.write_index(index, save_path)  
    
    with open(os.path.join(index_folder,f"{file_name}__metadata.pkl"), 'wb') as f:
        pickle.dump(metadata_store, f)
    
    return index, metadata_store

   
def query_faiss_index(file_base: str, query: str, top_k: int = 5):
    """
    Returns a list of dictionaries with complete metadata for each result
    Format: [
        {
            'id': str,
            'text': str,
            'page_number': str,
            'score': float,
            'metadata': dict (all original metadata)
        },
        ...
    ]
    """
    cwd=os.getcwd()#Current working directory
    index_folder=os.path.join(cwd,"indexed_pdfs")#Folder where files are indexed
    try:
        # Load index and metadata
        index = faiss.read_index(os.path.join(index_folder,f"{file_base}__index.faiss"))
        with open(os.path.join(index_folder,f"{file_base}__metadata.pkl"), 'rb') as f:
            metadata = pickle.load(f)
        
        # Create reverse mapping from FAISS index to ID
        id_lookup = {v['faiss_index']: k for k, v in metadata.items()}
        
        # Encode and search
        query_embedding = embedding_model.encode([query]).astype('float32')
        distances, indices = index.search(query_embedding, top_k)
        
        # Build results list
        results = []
        for i, idx in enumerate(indices[0]):
            if idx in id_lookup:
                id_ = id_lookup[idx]
                result_data = metadata[id_]
                results.append({
                    'id': id_,
                    'text': result_data['text'],
                    'page_number': result_data['metadata'].get('page_label', 
                                     result_data['metadata'].get('page_number', 'N/A')),
                    'score': float(distances[0][i]),
                    'metadata': result_data['metadata']  # All original metadata
                })
            else:
                results.append({
                    'id': f"missing_{idx}",
                    'text': f"Content not found for index {idx}",
                    'page_number': 'N/A',
                    'score': 0.0,
                    'metadata': {}
                })
        
        return results
    
    except Exception as e:
        print(f"Error during query: {e}")
        return []
      

"""
def  index_folder(all_files,chunk_size, chunk_overlap):
    #Index folder of pdf files
    #all_files=os.listdir(folder)#List of all PDF files
    print(all_files)
    for file in all_files:
        file_type=file.split(".")[-1]
        if file_type.lower()=="pdf":
            print(file)
            path=os.path.join(folder,file)#Path to PDF file
            print(path)                   
            file_name = os.path.splitext(os.path.basename(path))[0]#pdf filename

            # 1. Load document
            documents = llama_simple_reader(path)
               
            # 2. Chunk document
            nodes, record_dict = chunk_documents(file_name,documents, path, chunk_size, chunk_overlap)
              
            # 3. Generate embeddings
            embeddings, ids = embed_record_dict(record_dict, embedding_model)
                 
            # 4. Create index
            index, metadata_store = index_embeddings(embeddings, ids, record_dict, file_name)
"""
def index_folder(all_files_with_paths, chunk_size, chunk_overlap):
    for full_path in all_files_with_paths:
        file = os.path.basename(full_path)
        file_type = file.split(".")[-1]
        if file_type.lower() == "pdf":
            file_name = os.path.splitext(file)[0]

            # 1. Load document
            documents = llama_simple_reader(full_path)

            # 2. Chunk document
            nodes, record_dict = chunk_documents(file_name, documents, full_path, chunk_size, chunk_overlap)

            # 3. Generate embeddings
            embeddings, ids = embed_record_dict(record_dict, embedding_model)

            # 4. Create index
            index, metadata_store = index_embeddings(embeddings, ids, record_dict, file_name)
       

def query_gemini(task):
    # Query LLM
    query_state = ""
    TEXT = ""
    try:
        # Pass the API key directly as a string, not as a dictionary
        client = genai.Client(api_key=st.secrets["API_KEY"])
        # client = genai.Client(api_key=my_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=task
        )
        TEXT = str(response.text)
        # st.text(f"LLM:{TEXT}")
    except Exception as e:
        st.write(f"Unable to query llm: {e}")
        query_state = "error"
    return TEXT, query_state

#chunk_size=512
#chunk_overlap=50
#index_folder(PDF,chunk_size, chunk_overlap)
# 5. Query example
#query = "What caused the fall of Jerusalem?"
#results = query_faiss_index(file_name, query)

