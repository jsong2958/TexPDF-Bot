import os
import requests
import base64
import subprocess
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

BASE_DIR = os.path.join(os.getcwd(), "src")

def get_tex_name(path):
    return os.path.basename(path) if path.endswith(".tex") else None


def get_tex(path):
    url = "https://api.github.com/repos/jsong2958/uva-math-notes/contents/" + path
    headers = {
        "Accept": "vnd.github+json",
        "Authorization": "Bearer " + API_KEY
            }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        data = response.json()
        download_url = data["download_url"]

        tex = requests.get(download_url)
        tex_name = get_tex_name(path)
        
        file_path = os.path.join(BASE_DIR, tex_name)
        with open(file_path, "w") as file:
            file.write(tex.text)
            return

    else:
        print("get_tex failed:", response.status_code)


def compile_to_pdf(path):
    file = get_tex_name(path)
    print("BASE_DIR: ", BASE_DIR)
    os.chdir(BASE_DIR)
    print("CUR DIR: ", os.getcwd())
    subprocess.run(["pdflatex", "-halt-on-error", "-interaction=nonstopmode",
                    f"-output-directory={BASE_DIR}", "-output-format=pdf", file],
                    check=True)
    
def encode_pdf(pdf):
    with open(pdf, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")
    

def push_pdf(path, pdf):
    dir = path.split("/tex")[0]
    url = f"https://api.github.com/repos/jsong2958/uva-math-notes/contents/{dir}/pdf/{pdf}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + API_KEY
        }
    
    exists_file_response = requests.get(url, headers=headers)
    sha = None
    if exists_file_response.status_code == 200:
        sha = exists_file_response.json()["sha"]

    body = {
    
    
        "message": f"Update {get_tex_name(path).replace(".tex", ".pdf")}",
        "content": encode_pdf(pdf),
        "committer": {
            "name": "TexPDF-Bot",
            "email": "TexPDF@bot.com"
        }
    }

    if sha:
        body["sha"] = sha

    response = requests.put(url, headers=headers, json=body)
    if response.status_code == 200:
        data = response.json()
        print("PUSHED ", data["commit"]["message"])
    else:
        print(response.json())
    
def delete_files(name):
    dir = os.getcwd()
    for file in os.listdir(dir):
        if name in file:
            path = os.path.join(dir, file)
            os.remove(path)
            

