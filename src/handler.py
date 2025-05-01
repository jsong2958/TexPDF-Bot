from pdf_service import *
from global_state import GlobalState
import json

paths = GlobalState.paths

def save_response_to_file(resp):
    file_path = os.path.join(BASE_DIR, "data.json")
    with open(file_path, "w") as file:
        json.dump(resp, file, indent=4)

def load_response_file():
    file_path = os.path.join(BASE_DIR, "data.json")
    with open(file_path, "r") as file:
        return json.load(file)
    
def process_commit_data(data):
    global paths
    head_commit = data.get("head_commit")
    if not head_commit:
        return
    
    committer_name = head_commit.get("committer", {}).get("name", "")
    if committer_name == "TexPDF-Bot":
        print("Commit made by bot. Skipping.")
        return

    ref = data.get("ref", {})
    if "overleaf" in ref:
        print("Overleaf sync")
        return

    modified = head_commit.get("modified", [])
    added = head_commit.get("added", [])
    changed_files = modified + added
    
    for file in changed_files:
        if not file.endswith(".pdf") and file not in paths:
            paths.append(file)
        
       
def handle_tex(path):
    try:
        tex_name = get_tex_name(path)
        pdf_name = tex_name.replace(".tex", ".pdf")

        get_tex(path)
        compile_to_pdf(path)
        push_pdf(path, pdf_name)

        delete_files(pdf_name.replace(".pdf", ""))
    except Exception as e:
        print(f"Error processing file {path}: {e}")