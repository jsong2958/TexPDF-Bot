from flask import Flask, request
from handler import *
from global_state import GlobalState

app = Flask(__name__)

paths = GlobalState.paths

@app.route('/webhook', methods=['POST'])
def webhook():
    global paths
    data = request.get_json()
    
    save_response_to_file(data)
    response_data = load_response_file()
    process_commit_data(response_data)

    for path in paths:
        handle_tex(path)
    
    paths.clear()
    # save_response_to_file({})

    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)