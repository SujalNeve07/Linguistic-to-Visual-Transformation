import os
import base64
import logging
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from database import firebase_reference_manager
from image_matcher import image_matcher
from sketch_generator import sketch_generator

# -------------------------------------------------
# App setup
# -------------------------------------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Directories
# -------------------------------------------------
SAVE_DIR = r"D:\BE Final Year Project\forensic-sketch-matching\backend\saved_sketches"
os.makedirs(SAVE_DIR, exist_ok=True)
# -------------------------------------------------
# Members Dataset
# -------------------------------------------------
MEMBERS_DIR = r"D:\BE Final Year Project\forensic-sketch-matching\backend\datasets\members"
# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully"
    })
import mysql.connector
# DB CONNECTION
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root2",
        database="facetrace"
    )
def save_image(base64_data):
    import re

    folder = "static/sketches"
    os.makedirs(folder, exist_ok=True)

    # ✅ Remove metadata if present
    base64_data = re.sub('^data:image/.+;base64,', '', base64_data)

    filename = f"sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(folder, filename)

    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_data))

    return path

@app.route("/api/criminal/add", methods=["POST"])
def add_criminal():
    try:
        data = request.get_json()

        name = data.get("name")
        age = data.get("age")
        crime = data.get("crime")
        image_base64 = data.get("image")  # 🔴 rename for clarity

        # ✅ SAVE IMAGE FILE
        image_path = save_image(image_base64)

        conn = get_db()
        cursor = conn.cursor()

        query = """
        INSERT INTO criminals (name, age, crime, image)
        VALUES (%s, %s, %s, %s)
        """

        # ✅ STORE PATH instead of Base64
        cursor.execute(query, (name, age, crime, image_path))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Criminal saved",
            "image_path": image_path
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
# -------------------------------------------------
# Sketch generation API
# FRONTEND MUST CALL: /api/sketch/generate
# -------------------------------------------------
@app.route("/api/sketch/generate", methods=["POST"])
def api_generate_sketch():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({
                "status": "error",
                "message": "Prompt is required"
            }), 400

        logger.info(f"Generating sketch for prompt: {prompt}")

        # ✅ Call your sketch_generator module
        result = sketch_generator.generate_sketch(prompt)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        logger.error("Sketch generation error", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
@app.route("/api/utils/url-to-base64", methods=["POST"])
def url_to_base64():
    try:
        data = request.get_json()
        image_url = data.get("url")

        if not image_url:
            return jsonify({"error": "URL required"}), 400

        import requests
        import base64

        response = requests.get(image_url)
        response.raise_for_status()

        base64_image = base64.b64encode(response.content).decode("utf-8")

        return jsonify({
            "status": "success",
            "base64": base64_image
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# -------------------------------------------------
# Image matching
# -------------------------------------------------
@app.route("/api/match", methods=["POST"])
def match_images():

    data = request.get_json()

    generated_images = data.get("generatedImages", [])
    stored_images = data.get("storedImages", [])

    prompt = data.get("prompt", "").lower()

    use_members = "member" in prompt

    print("PROMPT :", prompt)
    print("USE MEMBERS :", use_members)

    results = image_matcher.match_images(
        generated_images,
        stored_images,
        use_members
    )

    formatted_results = []
    for result in results:
        formatted_results.append({
            "generated_image": f"data:image/jpeg;base64,{result['generated_image']}",
            "matches": [
                {
                    "similarity_score": m["similarity_score"],
                    "image": f"data:image/jpeg;base64,{m['image']}",
                    "path": m["path"]
                }
                for m in result["matches"]
            ]
        })

    return jsonify({"status": "success", "data": formatted_results})

# -------------------------------------------------
# Save generated sketch locally
# -------------------------------------------------
@app.route("/api/sketch/save", methods=["POST"])
def save_sketch():
    try:
        data = request.get_json()
        sketch_base64 = data.get("sketch")

        if not sketch_base64:
            return jsonify({
                "status": "error",
                "message": "No sketch data provided"
            }), 400

        if sketch_base64.startswith("data:image"):
            sketch_base64 = sketch_base64.split(",")[1]

        image_bytes = base64.b64decode(sketch_base64)

        filename = f"sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        return jsonify({
            "status": "success",
            "message": f"Sketch saved as {filename}"
        })

    except Exception as e:
        logger.error("Save sketch error", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# -------------------------------------------------
# Firebase reference image upload
# -------------------------------------------------
@app.route("/api/reference/upload", methods=["POST"])
def upload_reference_image():
    data = request.get_json()
    image_base64 = data.get("image")
    metadata = data.get("metadata", {})

    if not image_base64:
        return jsonify({
            "status": "error",
            "message": "No image provided"
        }), 400

    result = firebase_reference_manager.upload_reference_image(
        image_base64=image_base64,
        metadata=metadata
    )

    return jsonify(result)

# -------------------------------------------------
# Firebase reference image list
# -------------------------------------------------
@app.route("/api/reference/list", methods=["GET"])
def list_reference_images():
    limit = request.args.get("limit", 100, type=int)
    images = firebase_reference_manager.get_reference_images(limit=limit)

    return jsonify({
        "status": "success",
        "images": images
    })

# -------------------------------------------------
# Firebase reference image delete
# -------------------------------------------------
@app.route("/api/reference/delete/<image_id>", methods=["DELETE"])
def delete_reference_image(image_id):
    success = firebase_reference_manager.delete_reference_image(image_id)

    if success:
        return jsonify({
            "status": "success",
            "message": "Image deleted successfully"
        })

    return jsonify({
        "status": "error",
        "message": "Image not found"
    }), 404

# -------------------------------------------------
# App entry point
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
