from flask import Flask, request, jsonify
import socket

app = Flask(__name__)
hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname)

# Storage for messages
about = [
    {
        "board": "raspberry pi 5",
        "name": "Fridge Freshness Detector",
        "class": "Senior Design"
    }
]

messages = []


@app.route("/")
def home():
    try:
        return "Wow it actually worked!", 200
    except:
        return "", 404
    
@app.route("/test")
def whoami():
    try:
        return jsonify(about), 200
    except:
        return "", 404
    
if __name__ == "__main__":
    HOST = '0.0.0.0' # Use '0.0.0.0' to make the server accessible externally
    PORT = 5000  # Set your desired port number
    print("IP address: ", ipAddress)
    app.run(host=HOST, port=PORT, debug=True)
