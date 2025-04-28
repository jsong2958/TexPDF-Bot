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
        
        for file in head_commit.get("modified", []):
            if file.endswith(".pdf"):
                paths = []
                return
        
        paths = head_commit.get("modified", [])
        paths.extend(head_commit.get("added", []))





@app.route('/webhook', methods=['POST'])
def webhook():
    global paths
    data = request.get_json()
    write_json(data)
    print(f"Paths: {paths}")
    for path in paths:
        print(path)

        tex_name = get_tex_name(path)
        
        pdf = tex_name.replace(".tex", ".pdf")
        
        get_tex(path)
        compile_to_pdf(path)
        push_pdf(path, pdf)
        delete_files(pdf)

    paths = []
    with open("data.json", "w") as f:
        f.write("")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)