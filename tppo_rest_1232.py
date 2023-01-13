import argparse
from flask import Flask, render_template, request, jsonify
from src.server import RelayServer
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('./index.html')

# Get the current state of a specific relay
@app.route("/api/relay/<int:index>", methods=["GET"])
def get_state_by_index(index):
    state = relay_server.get_state(index)
    return jsonify({ "state": state })

# Update the state of a specific relay
@app.route("/api/relay/<int:index>", methods=["POST"])
def update_state_by_index(index):
    request_data = request.json.get("state")
    relay_server.save_state(request_data, index)
    state = relay_server.get_state(index)
    return jsonify(state)

# Get the current state of all relays
@app.route("/api/relay", methods=["GET"])
def get_state():
    state = relay_server.get_state()
    return jsonify({ "state": state })

# Update the state of all relays
@app.route("/api/relay", methods=["POST"])
def update_state():
    request_data = request.json.get("state")
    relay_server.save_state(request_data)
    state = relay_server.get_state()
    return jsonify(state)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Relay REST API",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--port", default=5000, type=int, help="Port number for the server")
    args = parser.parse_args()
    print(f'\033[95m------------------------------------------------------------\033[0m')
    print(f'\033[95mOpen http://localhost:{args.port}/ in your browser to see UI\033[0m')
    print(f'\033[95m------------------------------------------------------------\033[0m')
    try:
      loop = threading.Thread(target=app.run, kwargs={ "port": args.port, })
      loop.daemon = True
      loop.start()
      relay_server = RelayServer("0.0.0.0", 3000, "device.bson", "INFO")
      relay_server.start()
    except KeyboardInterrupt:
        print("Shutting down...")