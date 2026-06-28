import logging
from flask import Flask, request, jsonify
import joblib
import numpy as np
import warnings 

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

try:
    model_pipeline = joblib.load("loan_approval.pkl")
    logging.info("Pipeline loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load pipeline: {e}")
    model_pipeline = None

# Added a readiness probe endpoint for Docker/Kubernetes container orchestration
@app.route('/health', methods=['GET'])
def health_check():
    if model_pipeline:
        return jsonify({'status': 'healthy'}), 200
    return jsonify({'status': 'unhealthy', 'reason': 'model missing'}), 503

@app.route('/predict', methods=['POST'])
def predict():
    if not model_pipeline:
        return jsonify({'error': 'Pipeline not loaded on server.'}), 500

    try:
        data = request.json
        
        # KEY FIX: Clean keys without spaces to match standard JSON/API practices
        expected_keys = [
            'no_of_dependents', 'education', 'self_employed', 
            'income_annum', 'loan_amount', 'loan_term', 'cibil_score', 
            'residential_assets_value', 'commercial_assets_value', 
            'luxury_assets_value', 'bank_asset_value'
        ]
        
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            return jsonify({'error': f'Bad Request. Missing JSON keys: {missing_keys}'}), 400

        features = np.array([[data[key] for key in expected_keys]])

        # The Pipeline handles the StandardScaler automatically internally
        prediction = model_pipeline.predict(features)
        probability = model_pipeline.predict_proba(features)

        result = "Loan Rejected" if prediction[0] == 1 else "Loan Approved"
        confidence = round(float(np.max(probability) * 100), 2)

        return jsonify({
            'prediction': result, 
            'confidence': f"{confidence}%"
        }), 200

    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error during prediction.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)