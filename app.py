from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(
    __name__,
    static_folder="build",
    static_url_path=""
)

CORS(app)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

@app.route("/health")
def health():
    try:
        uri = os.environ.get("MONGO_URI")
        return {
            "status": "ok",
            "mongo_uri_exists": uri is not None,
            "mongo_uri_preview": uri[:30] if uri else "NONE"
        }
    except Exception as e:
        return {"error": str(e)}, 500

# ---------------- API ROUTES ----------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = []
    for task in mongo.db.tasks.find():
        tasks.append({
            "_id": str(task["_id"]),
            "title": task["title"]
        })
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    mongo.db.tasks.insert_one({"title": data["title"]})
    return jsonify({"message": "Task created"})

@app.route("/tasks/<id>", methods=["PUT"])
def update_task(id):
    data = request.json
    mongo.db.tasks.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"title": data["title"]}}
    )
    return jsonify({"message": "Task updated"})

@app.route("/tasks/<id>", methods=["DELETE"])
def delete_task(id):
    mongo.db.tasks.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Task deleted"})

# ---------------- FRONTEND ----------------

@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run()
