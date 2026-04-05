from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# In-memory database
database = {}
lock = threading.Lock()


# -----------------------
# CREATE
# -----------------------
@app.route('/data', methods=['POST'])
def create():
    data = request.json
    with lock:
        record_id = len(database) + 1
        database[record_id] = data
    return jsonify({"msg": "created", "id": record_id}), 200


# -----------------------
# READ
# -----------------------
@app.route('/data/<int:id>', methods=['GET'])
def read(id):
    if id in database:
        return jsonify(database[id]), 200
    return jsonify({"error": "not found"}), 404


# -----------------------
# UPDATE
# -----------------------
@app.route('/data/<int:id>', methods=['PUT'])
def update(id):
    data = request.json
    with lock:
        if id in database:
            database[id].update(data)
            return jsonify({"msg": "updated"}), 200
    return jsonify({"error": "not found"}), 404


# -----------------------
# DELETE
# -----------------------
@app.route('/data/<int:id>', methods=['DELETE'])
def delete(id):
    with lock:
        if id in database:
            del database[id]
            return jsonify({"msg": "deleted"}), 200
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
