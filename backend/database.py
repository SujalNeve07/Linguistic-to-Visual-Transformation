import firebase_admin
from firebase_admin import credentials, db, storage
import os
import base64
from datetime import datetime
import uuid


class FirebaseReferenceImageManager:
    def __init__(self):
        # Initialize Firebase only once
        if not firebase_admin._apps:
            # ✅ UPDATED: Correct local path to Firebase key
            cred_path = r"D:\BE Final Year Project\forensic-sketch-matching\backend\firebase-key.json.json"

            cred = credentials.Certificate(cred_path)

            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://facetrace-bf2de-default-rtdb.firebaseio.com/",
                "storageBucket": "facetrace-bf2de.appspot.com"
            })

        # Initialize database and storage references
        self.db = db.reference("reference_images")
        self.storage_bucket = storage.bucket()

    def upload_reference_image(self, image_base64, metadata=None):
        try:
            filename = f"reference_{uuid.uuid4().hex}.png"
            image_bytes = base64.b64decode(image_base64)

            blob = self.storage_bucket.blob(f"reference_images/{filename}")
            blob.upload_from_string(image_bytes, content_type="image/png")

            # Make image public (OK for local project)
            blob.make_public()

            image_metadata = {
                "filename": filename,
                "public_url": blob.public_url,
                "uploaded_at": datetime.now().isoformat(),
                "additional_metadata": metadata or {}
            }

            ref = self.db.push(image_metadata)

            return {
                "id": ref.key,
                "url": blob.public_url,
                "status": "success"
            }

        except Exception as e:
            print("Firebase upload error:", e)
            return {
                "status": "error",
                "message": str(e)
            }

    def get_reference_images(self, limit=100):
        try:
            images = self.db.limit_to_last(limit).get()
            return list(images.values()) if images else []
        except Exception as e:
            print("Error retrieving images:", e)
            return []

    def delete_reference_image(self, image_id):
        try:
            image_metadata = self.db.child(image_id).get()
            if not image_metadata:
                return False

            if "filename" in image_metadata:
                blob = self.storage_bucket.blob(
                    f"reference_images/{image_metadata['filename']}"
                )
                blob.delete()

            self.db.child(image_id).delete()
            return True

        except Exception as e:
            print("Deletion error:", e)
            return False


# Singleton instance
firebase_reference_manager = FirebaseReferenceImageManager()