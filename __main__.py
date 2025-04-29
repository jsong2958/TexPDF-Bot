from flask import Flask, request
import json
from test import *

app = Flask(__name__)

paths = []

def write_json(resp):
    global paths
    with open("data.json", "w") as file:
        json.dump(resp, file, indent=4)
    with open("data.json", "r") as file:
        data = json.load(file)

        head_commit = data.get("head_commit")
        if not head_commit:
            paths = []
            return
        
        committer_name = head_commit.get("committer", {}).get("name", "")
        if committer_name == "TexPDF-Bot":
            print("Commit made by bot. Skipping.")
            paths = []
            return

        modified = head_commit.get("modified", [])
        added = head_commit.get("added", [])
        changed_files = modified + added

        if all(file.endswith(".pdf") for file in changed_files):
            paths = []
            return
        
        paths = [file for file in changed_files if not file.endswith(".pdf")]
        
       


@app.route('/webhook', methods=['POST'])
def webhook():
    global paths
    data = request.get_json()
    write_json(data)
    print(f"Paths: {paths}")
    for path in paths:
        print(path)
        with open("xd.json", "w") as f:
            json.dump(data, f, indent=4)
        try:
            tex_name = get_tex_name(path)
        except Exception as e:
            print(f"Error for get_tex_name: {e}")

        try:
            pdf = tex_name.replace(".tex", ".pdf")
        except Exception as e:
            print(f"Error for replace .tex with .pdf: {e}")

        try:
            get_tex(path)
        except Exception as e:
            print(f"Error for get_tex: {e}")

        try:
            compile_to_pdf(path)
        except Exception as e:
            print(f"Error for compile_to_pdf: {e}")

        try:
            push_pdf(path, pdf)
        except Exception as e:
            print(f"Error for push_pdf: {e}")

        try:
            pdf = pdf.replace(".pdf", "")
            delete_files(pdf)
        except Exception as e:
            print(f"Error for delete_files: {e}")

    paths = []
    # with open("data.json", "w") as f:
    #     f.write("")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)