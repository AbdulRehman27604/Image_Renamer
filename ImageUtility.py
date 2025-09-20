import os
import subprocess
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Use /tmp when running on Render (safe writable directory)
if os.environ.get("RENDER"):
    BASE_DIR = "/tmp"
else:
    BASE_DIR = os.getcwd()

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ZIP_FOLDER = os.path.join(BASE_DIR, "downloads")
SCRIPT_PATH = os.path.join(BASE_DIR, "imageRenamer.sh")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    zip_path = None

    if request.method == "POST":
        uploaded_files = request.files.getlist("images")
        if not uploaded_files:
            return render_template("index.html", output="No files uploaded!")

        # Check if exiftool exists
        if subprocess.call(["which", "exiftool"]) != 0:
            return render_template("index.html", output="Error: exiftool is not installed on the server!")

        # Clear previous uploads
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

        # Save uploaded files
        for file in uploaded_files:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

        # Run bash script
        try:
            result = subprocess.run(
                [SCRIPT_PATH, UPLOAD_FOLDER],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Error running script:\n{e.stderr}"

        # Create zip of renamed images
        zip_path = os.path.join(ZIP_FOLDER, "renamed_images.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_name in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, file_name)
                zipf.write(file_path, arcname=file_name)

    return render_template("index.html", output=output, zip_path=zip_path)

@app.route("/download")
def download():
    zip_path = os.path.join(ZIP_FOLDER, "renamed_images.zip")
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return "No file available"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
