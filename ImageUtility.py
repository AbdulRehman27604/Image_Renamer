from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        folder = request.form.get("folder_path")

        # Check if folder exists
        if not os.path.isdir(folder):
            output = f"Folder does not exist: {folder}"
        else:
            # Call your bash script
            try:
                result = subprocess.run(
                    ["./imageRenamer.sh", folder],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = result.stdout
            except subprocess.CalledProcessError as e:
                output = f" Error:\n{e.stderr}"

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)

