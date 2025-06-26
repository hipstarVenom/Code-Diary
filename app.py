from flask import Flask, render_template, request, jsonify, send_file
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId

import io

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["code_diary"]
entries = db["entries"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/enter")
def enter():
    return render_template("enter.html")

@app.route("/view")
def view():
    return render_template("view.html")

@app.route("/add", methods=["POST"])
def add_entry():
    data = request.get_json()
    entries.insert_one(data)
    return jsonify({"status": "success"})

@app.route("/entries")
def get_entries():
    all_entries = list(entries.find())
    for e in all_entries:
        e["_id"] = str(e["_id"])
    return jsonify(all_entries)

@app.route("/delete/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    entries.delete_one({"_id": ObjectId(entry_id)})
    return jsonify({"status": "deleted"})

@app.route("/edit/<entry_id>", methods=["PUT"])
def edit_entry(entry_id):
    data = request.get_json()
    entries.update_one({"_id": ObjectId(entry_id)}, {"$set": data})
    return jsonify({"status": "updated"})

@app.route("/export/txt")
def export_txt():
    entries_data = list(entries.find())
    lines = ["📓 Code Diary - Exported Entries\n"]

    for entry in entries_data:
        lines.append(f"Date: {entry.get('date', '')}")
        lines.append(f"Tech: {entry.get('tech', '')}")
        lines.append(f"Note: {entry.get('note', '')}")
        lines.append(f"Bugs: {entry.get('bugs', '')}")
        lines.append(f"Fixes: {entry.get('fixes', '')}")
        lines.append("-" * 40)

    text_content = "\n".join(lines)
    buffer = io.BytesIO(text_content.encode("utf-8"))

    return send_file(
        buffer,
        as_attachment=True,
        download_name="code_diary.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(debug=True)
