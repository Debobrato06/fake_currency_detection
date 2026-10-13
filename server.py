from flask import Flask, render_template, request, jsonify

from detector import analyze_currency, model_info

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024  # 40 MB for up to ~6 phone photos


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    return jsonify(model_info())


@app.route('/analyze', methods=['POST'])
def analyze():
    files = [f for f in request.files.getlist('file') if f and f.filename]
    if not files:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        threshold = float(request.form.get('threshold', 0.7))
    except ValueError:
        threshold = 0.7
    threshold = min(max(threshold, 0.5), 0.99)

    results, error = analyze_currency([f.read() for f in files], threshold=threshold)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=False, port=5000)
