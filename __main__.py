from flask import Flask, request
import json
from test import *

app = Flask(__name__)

paths = []

def save_response_to_file(resp):
    with open("data.json", "w") as file:
        json.dump(resp, file, indent=4)

def load_response_file():
    with open("data.json", "r") as file:
        return json.load(file)
    
def process_commit_data(data):
    global paths

    head_commit = data.get("head_commit")
    if not head_commit:
        paths = []
        return
    
    committer_name = head_commit.get("committer", {}).get("name", "")
    if committer_name == "TexPDF-Bot":
        print("Commit made by bot. Skipping.")
        paths = []
        return

    ref = data.get("ref", {})
    if "overleaf" in ref:
        print("Overleaf sync")
        paths = []
        return

    modified = head_commit.get("modified", [])
    added = head_commit.get("added", [])
    changed_files = modified + added

    if all(file.endswith(".pdf") for file in changed_files):
        paths = []
        return
    
    paths = [file for file in changed_files if not file.endswith(".pdf")]
        
       
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

@app.route('/webhook', methods=['POST'])
def webhook():
    global paths
    data = request.get_json()
    
    save_response_to_file(data)
    response_data = load_response_file()
    process_commit_data(response_data)

    for path in paths:
        handle_tex(path)
    
    paths = []
    save_response_to_file({})

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)