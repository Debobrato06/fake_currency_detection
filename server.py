from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    image_bytes = file.read()
    
    # Try elite analysis, fallback to legacy if needed
    try:
        from detector import analyze_currency_elite
        results, error = analyze_currency_elite(image_bytes)
    except ImportError:
        from detector import analyze_currency
        results, error = analyze_currency(image_bytes)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
