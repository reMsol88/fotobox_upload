from datetime import datetime
from flask import Flask, request, jsonify
import os
from PIL import Image
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import dotenv
import logging
# Set up logging
logging.basicConfig(level=logging.DEBUG)
# Load environment variables from .env file
dotenv.load_dotenv()

# Configuration
cloudinary.config(
    cloud_name="dhkhinrl2",
    api_key="488992739588361",
    api_secret=os.getenv("CLOUDINARY_SECRET"),  # Click 'View API Keys' above to copy your API secret
    secure=True
)

app = Flask(__name__)

UPLOAD_DIR = "./uploads"
FRAME_DIR = "./frames"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "API is running"})

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
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

    print(f"Upload: {file.filename}, frame_type={frame_type}")

    # Speichere das Originalbild immer (aber gespiegelt!)
    with Image.open(temp_location) as img:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img.save(file_location)

        upload_result = cloudinary.uploader.upload(file_location, public_id=base_name)
        logging.info(f"Uploaded image URL: {upload_result['secure_url']}")
        # Wenn frame_type gesetzt ist, speichere zusätzlich das Bild mit Rahmen
        if frame_type:
            frame_path = os.path.join(FRAME_DIR, frame_type)
            if os.path.isfile(frame_path):
                with Image.open(frame_path) as frame:
                    frame = frame.resize(img.size, Image.LANCZOS)
                    img_with_frame = img.copy()
                    img_with_frame.paste(frame, (0, 0), frame)
                    frame_location = os.path.join(UPLOAD_DIR, f"{base_name}_frame{ext}")
                    img_with_frame.save(frame_location)
                    upload_result = cloudinary.uploader.upload(frame_location, public_id=f"{base_name}_frame")
                    logging.info(f"Uploaded framed image URL: {upload_result['secure_url']}")
            else:
                print(f"Frame file not found: {frame_path}")
    os.remove(temp_location)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render stellt PORT bereit
    app.run(host="0.0.0.0", port=port, debug=True)  # Setze debug=True für Entwicklungszwecke