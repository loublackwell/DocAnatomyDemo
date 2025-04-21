import streamlit as st
import os
import pickle
import numpy as np
import faiss
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from google import genai

#Initialization of varibales
#global my_key
cwd = os.getcwd()  # Current working directory
PDF = os.path.join(cwd, "PDF")  # List of pdf files
chunk_file=os.path.join(cwd,"chunk_stats.json")#file containing the chunk and overl size metadata for each file
#my_key=""#Add your Gemni API key here

def llama_simple_reader(path):
    #Read PDF file
    try:
        documents = SimpleDirectoryReader(input_files=[path]).load_data()
        return documents
    except Exception as e:
        print(f"Unable to read: {path}: {e}")
        return []

def chunk_documents(file_name, documents, path, chunk_size, chunk_overlap):
    #Split the document given the chunk size and chunk overlap.
    record_dict = {}
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = parser.get_nodes_from_documents(documents)
    for pos, node in enumerate(nodes):
        ID = f"{file_name}_{pos}"
        record_dict[ID] = node
    return nodes, record_dict

def embed_record_dict(record_dict, embedding_model):
    #Generate embeddings
    embeddings = []
    ids = []
    for doc_id, node in record_dict.items():
        text = node.text#Return text
        embedding = embedding_model.encode(text, show_progress_bar=False)
        embeddings.append(embedding)
        ids.append(doc_id)#List of document/record IDs
    return embeddings, ids

def index_embeddings(embeddings, ids, record_dict, file_name):
    cwd = os.getcwd()  # Current working directory
    index_folder = os.path.join(cwd, "indexed_pdfs")  # Folder where files are indexed
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
    save_path = os.path.join(index_folder, f"{file_name}__index.faiss")  # Save path
    faiss.write_index(index, save_path)  
    
    with open(os.path.join(index_folder, f"{file_name}__metadata.pkl"), 'wb') as f:
        pickle.dump(metadata_store, f)
    
    return index, metadata_store

def query_faiss_index(embedding_model,file_base, query, top_k):
    #Query Faiss index given as input the base filename,query and the number of result to return.
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
    cwd = os.getcwd()  # Current working directory
    index_folder = os.path.join(cwd, "indexed_pdfs")  # Folder where files are indexed
    try:
        # Load index and metadata
        index = faiss.read_index(os.path.join(index_folder, f"{file_base}__index.faiss"))
        with open(os.path.join(index_folder, f"{file_base}__metadata.pkl"), 'rb') as f:
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
      

def index_folder(embedding_model,all_files, chunk_size, chunk_overlap):
    # Index folder of pdf files
    for file in all_files:
        file_type = file.split(".")[-1]
        if file_type.lower() == "pdf":
            path = os.path.join(PDF, file)  # Path to PDF file                   
            file_name = os.path.splitext(os.path.basename(path))[0]  # pdf filename

            # 1. Load document
            documents = llama_simple_reader(path)
               
            # 2. Chunk document
            nodes, record_dict = chunk_documents(file_name, documents, path, chunk_size, chunk_overlap)
              
            # 3. Generate embeddings
            embeddings, ids = embed_record_dict(record_dict, embedding_model)
                 
            # 4. Create index
            index, metadata_store = index_embeddings(embeddings, ids, record_dict, file_name)

# Function to re-index a PDF file
def reindex_pdf(file_name, chunk_size, chunk_overlap):
    """
    Function to re-index a single PDF file with the specified chunk size and overlap.
    """
    pdf_folder = os.path.join(os.getcwd(), "PDF")
    file_path = os.path.join(pdf_folder, f"{file_name}.pdf")
    
    # Re-index the file
    documents = llama_simple_reader(file_path)
    
    # Chunk the document
    nodes, record_dict = chunk_documents(file_name, documents, file_path, chunk_size, chunk_overlap)
    
    # Generate embeddings and create the index
    embeddings, ids = embed_record_dict(record_dict, embedding_model)
    index, metadata_store = index_embeddings(embeddings, ids, record_dict, file_name)

    # Display a success message
    st.success(f"Re-indexed {file_name}.pdf with chunk size {chunk_size} and chunk overlap {chunk_overlap}.")


def chunk_stats(chunk_path,PDF):
    #Get chunk stats for each file and return to UI    
    #Initial/default chunk and overlap
    if not os.path.isfile(chunk_path):
        stats_dict={}
        all_pdfs=os.listdir(PDF)#List of pdf files
        for file in all_pdfs:
            file_type=file.split(".")[-1]#File type
            if file_type.lower()=="pdf":
                stats_dict[file]={"chunk":512,"overlap":50}
        viewJson=json.dumps(stats_dict,indent=2,ensure_ascii=False)
        with open(chunk_path,"w") as f:
            f.write(viewJson)
    else:
        #Retrieve chunk and overlap stats
        with open(chunk_path,"r") as f:
            stats_dict=json.loads(f.read())
    return stats_dict

        
def query_gemini(task):
    # Query LLM. Takes as input the task definitiion and returns the LLM response.
    query_state = ""
    TEXT = ""
    try:
        # Pass the API key directly as a string, not as a dictionary
        client = genai.Client(api_key=st.secrets["API_KEY"])
        #client = genai.Client(api_key=my_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=task
        )
        TEXT = str(response.text)
        # st.text(f"LLM:{TEXT}")
    except Exception as e:
        st.write(f"Unable to query llm: {e}")
        query_state = "error"
    return TEXT, query_state

def build_prompt(expert, verses,question):
    task = f"""{expert} who has been given the following task:
             Based on the following question:
             Question:
             {question}
             
             Does the TEXT below support answering the question above? Answer YES or NO.
             
             CONSIDERATIONS:
             1. No Hallucinations allowed. Stick with completing the task given the provided context.
             2. Only use the text to serach for answers
             3. The output should be a valid python dictionary.
             4. Do not escape any of the characters.
             6. Enclose key value pair in double quotes
                         
             OUTPUT FORMAT:
             ```
             {{"ANSWER":[YES or NO]}}
             ```
             TEXT
             {verses}
          """
    return task

def conlcusion(question, answers):
    #Build conclusion task for LLM for the summary prompt.
    task2 = f"""Review the list of potential answers to the following question and see if there is an answer that 
                can be found from the list. If there are answers found, summarize in no more than 5 sentences.
                QUESTION:
                {question}. 
                POTENTIAL ANSWERS:
                {answers}

                CONSIDERATIONS:
                 1. No Hallucinations allowed. Stick with completing the task given the provided context.
                 2. Only use the list of text to search for answers
                 3. The output should be a valid python dictionary or JSON format
                 4. Do not provide/derive any answers that were not originally mentioned in the potential answers.
                 5. List the texts that you used to come to the answers.
                 6. If the question or task is not clear, state that in the ANSWER when returning your answer.
                 7. Provide concise answers whenever possible.
                 8. Remove any duplicate answers.
                 9. Use single quotes for all fields inside the dictionary
                 10. replace all quotations with and * symbol.
                 11. Only return one dictionary
                 12. Use double quotate symbol for all key value pairs.
            
                OUTPUT FORMAT:
                    ```
                     {{"ANSWER":[<insert any summary here>],"JUSTIFICATION":["<list of any of the dictionaries that you used to get the answer>",....]}}
                     ```

                """
    return task2


def parse_llm(out):
    #Parse LLM output and remove noise
    block=""
    out1 = str(out)            
    out2 = out1.replace("\\n", "")
    out = out2.replace("\n", "")
    start = out.find("{")
    end = out.rfind("}")
    if start and end > -1:
        block = out[start:end+1]        
    return block

def display_results(out2,text_dict):
    # Display the parsed query results
    try:
        pydict = json.loads(out2)  # Return dictionary
        summary = pydict.get("ANSWER")
        justification = pydict.get("JUSTIFICATION")

        # Summary
        if summary:
            st.write("**AI Summary**")
            if isinstance(summary,str):
                st.write(summary)
                st.write("---")  # Horizontal line for separation
                
                # Supporting documents    
                if isinstance(justification,list):
                    st.write("**Supporting Records**")
                    for doc in justification:
                        doc_metadata = doc.split("-")
                        page = doc_metadata[0]
                        score = round((float(doc_metadata[1])), 2)
                        ID=str(doc_metadata[2])
                        text =text_dict[ID]#Get original text
                
                        with st.expander(f"📄 Page {page} | Score: {score} | {text[:50]}..."):
                            st.write(f"**Page {page}** (Relevance score: {score})")
                            st.write("")  # Blank line
                            st.write(text)
                else:
                    st.write(f"**{pydict}")
                    
            #Summary not available    
            if isinstance(summary,list):
                st.write(summary[0])
            
            
    except Exception as e:
        pydict = {}
        st.write(f"Error: {str(e)}")
    

# Streamlit UI
def main():
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')#Embedding model
    stats_dict=chunk_stats(chunk_file,PDF)
    # List all PDF files in the 'PDF' folder
    pdf_folder = os.path.join(os.getcwd(), "PDF")
    all_files = [f[:-4] for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    # Sidebar: File selection, chunk size, and chunk overlap inputs
    st.sidebar.header("Re-index PDF File")
    
    # File selection dropdown
    selected_file = st.sidebar.selectbox("Choose a file to re-index", all_files)
    
    # Chunk size and overlap sliders
    chunk_size = st.sidebar.slider("Choose chunk size", min_value=128, max_value=1024, value=512, step=128)
    chunk_overlap = st.sidebar.slider("Choose chunk overlap", min_value=0, max_value=100, value=50, step=10)

    #Number of results to return
    top_k = st.sidebar.slider("Number of documents to return", min_value=1, max_value=20, value=5)
     
    # Show full stats table in sidebar
    st.sidebar.subheader("📊 Indexing Stats")
    stats_df = pd.DataFrame.from_dict(stats_dict, orient="index")
    stats_df.index.name = "File"
    stats_df.columns = ["Chunk Size", "Overlap"]
    st.sidebar.dataframe(stats_df)    

    # Re-index button
    if st.sidebar.button(f"Re-index {selected_file}.pdf"):
        original_filename=f"{selected_file}.pdf"
        reindex_pdf(selected_file, chunk_size, chunk_overlap)
        stats_dict[original_filename]={"chunk":chunk_size,"overlap":chunk_overlap}
        viewJson=json.dumps(stats_dict,indent=2,ensure_ascii=False)
        #Save updated chunk metadata
        with open("chunk_stats.json","w") as f:
            f.write(viewJson)
        

    # Query section (optional, depending on the rest of your UI)
    st.title("PDF Indexing and RAG Querying")
    query = st.text_input("Enter your query:")
    
    if query:
        final_list=[]
        text_dict={}
        # Here you can call the query function with the selected file
        st.write(f"Querying {selected_file}.pdf with your input: {query}")
        results = query_faiss_index(embedding_model,selected_file,query, top_k) #file_base: str, query: str, top_k: int = 5
        #st.write(results[0])
        
        #Display results
        #Loop thru each result
        for result in results:
            ID=result["id"]            #Document ID
            answer=result['text'] #Text from record
            score=result['score']                #Confidence score for match
            page=result["page_number"] #Match page number
            text_dict[ID]=answer                #Stores original text in dictionary
            expert="You are a college professor with phd in linguistics and physics."
            #record={"page":page,"score":score,"text":answer}
            final_list.append(f"{page}-{score}-{ID}-{answer}")
            #final_list.append(record)#List of results
                    
        #LLM Conclusion Task given query and list of answers--
        task=conlcusion(query,  final_list)#LLM task for determining conclusion
        out=query_gemini(task)#Query LLM
        out=parse_llm(out)#Parse LLM results
        out2=out.replace('\\', '\\\\')
        display_results(out2,text_dict)


if __name__ == "__main__":
    main()
