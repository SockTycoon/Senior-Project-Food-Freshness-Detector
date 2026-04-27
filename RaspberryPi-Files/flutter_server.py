from flask import Flask, jsonify, request
import time

app = Flask(__name__)


@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Server is running!"
    }), 200



@app.route('/api/run-debug', methods=['POST'])
def run_debug():
    data = request.get_json()

    if not data or 'action' not in data:
        return jsonify({
            "message": "Invalid request"
        }), 400

    action = data['action']

    if action == 'run_program':
        try:
            # Simulate air quality test
            time.sleep(2)  

            # Replace this with actual hardware / script call
            return jsonify({
                "message": "Air quality test ran successfully"
            }), 200

        except Exception as e:
            return jsonify({
                "message": f"Execution failed: {str(e)}"
            }), 500

    return jsonify({
        "message": "Unknown action"
    }), 400


if __name__ == '__main__':
    # IMPORTANT: allow external connections (Flutter device access)
    app.run(host='0.0.0.0', port=5000, debug=True)