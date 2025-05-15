from flask import Flask, render_template, request, send_file
import pandas as pd
import re
import io

app = Flask(__name__)

def extract_ids(file, id_type):
    df = pd.read_csv(file)
    pattern = r'\b([12]\d{9})\b' if id_type == '10' else r'\b(14\d{6})\b'
    ids = []
    for col in df.columns:
        for cell in df[col]:
            ids.extend(re.findall(pattern, str(cell)))
    return ids

@app.route("/", methods=["GET", "POST"])
def index():
    ids = []
    if request.method == "POST":
        file = request.files["file"]
        id_type = request.form["id_type"]
        ids = extract_ids(file, id_type)
        return render_template("index.html", ids=ids, count=len(ids))
    return render_template("index.html", ids=[])

@app.route("/download", methods=["POST"])
def download():
    ids = request.form.getlist("ids")
    df = pd.DataFrame(ids, columns=["ID"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="extracted_ids.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
