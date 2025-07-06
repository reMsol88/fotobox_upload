from datetime import datetime
from flask import Flask, request, jsonify
import os
from PIL import Image

app = Flask(__name__)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "API is running"})

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    with_frame = request.form.get("with_frame")
    frame_type = request.form.get("frame_type")

    if not file:
        return "No file uploaded", 400

    _, ext = os.path.splitext(file.filename)
    ext = ext if ext else ".jpg"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = f"photo_{timestamp}"
    file_location = os.path.join(UPLOAD_DIR, f"{base_name}{ext}")

    # Speichere das Originalbild temporär
    temp_location = file_location + ".tmp"
    file.save(temp_location)

    with_frame_bool = with_frame == "1"
    print(f"Upload: {file.filename}, with_frame={with_frame_bool}, frame_type={frame_type}")

    # Speichere das Originalbild immer (aber gespiegelt!)
    with Image.open(temp_location) as img:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img.save(file_location)

        # Wähle das passende Frame-Bild
        if frame_type == "flamingo1":
            frame_path = "./flamingo1.png"
        else:
            frame_path = "./flamingo.png"

        # Wenn Rahmen gewünscht, speichere zusätzlich das Bild mit Rahmen
        if with_frame_bool:
            with Image.open(frame_path) as frame:
                frame = frame.resize(img.size, Image.LANCZOS)
                img_with_frame = img.copy()
                img_with_frame.paste(frame, (0, 0), frame)
                frame_location = os.path.join(UPLOAD_DIR, f"{base_name}_frame{ext}")
                img_with_frame.save(frame_location)
    os.remove(temp_location)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)