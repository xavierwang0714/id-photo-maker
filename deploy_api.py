# deploy_api.py

import os
from flask import Flask, request, jsonify
from id_photo_maker import UPLOAD_FOLDER, AHEAD, NO_HUMAN_FACE
from id_photo_maker import generate_id_photo, add_background_color, generate_layout_photo, add_watermark, human_matting
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

# 创建日志记录器
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    ahead = request.headers.get('ahead')
    if ahead not in AHEAD:
        logger.error(f"Invalid ahead in header: {ahead}")
        return jsonify({'error': 'Invalid ahead in header'}), 400

    # Check if the post request has the file part
    if 'file' not in request.files:
        logger.error('No file part')
        return jsonify({'error': 'No file part'}), 400

    # Get the file
    file = request.files['file']
    if file.filename == '':
        logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    response_json = None

    if ahead == AHEAD[0]:  # ID photo
        color = request.headers.get('color')

        # Generate ID photo with transparent background
        try:
            _, image_path = generate_id_photo(file_path)
        except Exception as e:
            if str(e) == NO_HUMAN_FACE:  # No human face detected
                return jsonify({'error': 'No human face detected'}), 477

            logger.error(f"Error generating ID photo: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # Add background color
        try:
            response_json, image_path = add_background_color(image_path, color)
        except Exception as e:
            logger.error(f"Error adding background color: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        return jsonify({'message': 'File uploaded successfully', 'imageData': response_json["image_base64"]}), 200
    elif ahead == AHEAD[1]:  # Human matting
        try:
            response_json, _ = human_matting(file_path)
        except Exception as e:
            logger.error(f"Error human matting: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        return jsonify({'message': 'File uploaded successfully', 'imageData': response_json["image_base64"]}), 200
    elif ahead == AHEAD[2]:  # Layout photo
        color = request.headers.get('color')

        # Generate ID photo with transparent background
        try:
            _, image_path = generate_id_photo(file_path)
        except Exception as e:
            if str(e) == NO_HUMAN_FACE:  # No human face detected
                return jsonify({'error': 'No human face detected'}), 477

            logger.error(f"Error generating ID photo: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # Add background color
        try:
            _, image_path = add_background_color(image_path, color)
        except Exception as e:
            logger.error(f"Error adding background color: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # Generate layout photo
        try:
            response_json, image_path = generate_layout_photo(image_path)
        except Exception as e:
            logger.error(f"Error generating layout photo: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        return jsonify({'message': 'File uploaded successfully', 'imageData': response_json["image_base64"]}), 200
    elif ahead == AHEAD[3]:  # Watermark
        watermark_text = request.headers.get('watermark')
        try:
            response_json, _ = add_watermark(file_path, watermark_text)
        except Exception as e:
            logger.error(f"Error add watermark: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        return jsonify({'message': 'File uploaded successfully', 'imageData': response_json["image_base64"]}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)