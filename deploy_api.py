# deploy_api.py

import os
from datetime import datetime
import pytz
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

    # 检查是否有文件
    if 'file' not in request.files:
        logger.error('No file part')
        return jsonify({'error': 'No file part'}), 400

    # 获取文件
    file = request.files['file']
    if file.filename == '':
        logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    # 生成文件名
    shanghai_tz = pytz.timezone("Asia/Shanghai")
    current_time = datetime.now(shanghai_tz).strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{current_time}.jpg"

    # 保存文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file_path = os.path.normpath(file_path)  # 标准化路径
    file.save(file_path)

    response_json = None

    if ahead == AHEAD[0]:  # ID photo
        color = request.headers.get('color')

        # 生成透明背景的照片
        try:
            _, image_path = generate_id_photo(file_path)
        except Exception as e:
            if str(e) == NO_HUMAN_FACE:  # No human face detected
                return jsonify({'error': 'No human face detected'}), 477

            logger.error(f"Error generating ID photo: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # 添加背景颜色
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

        # 生成透明背景的照片
        try:
            _, image_path = generate_id_photo(file_path)
        except Exception as e:
            if str(e) == NO_HUMAN_FACE:  # No human face detected
                return jsonify({'error': 'No human face detected'}), 477

            logger.error(f"Error generating ID photo: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # 添加背景颜色
        try:
            _, image_path = add_background_color(image_path, color)
        except Exception as e:
            logger.error(f"Error adding background color: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # 生成排版照
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
