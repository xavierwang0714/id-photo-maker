# functions.py

import base64
import os
import requests
from datetime import datetime
from .config import (color_dict, ADD_BACKGROUND_COLOR_PATH, ID_PHOTO_PATH, LAYOUT_PHOTO_PATH, WATERMARK_PATH,
                     NONE_BACKGROUND_FOLDER, WITH_BACKGROUND_FOLDER, LAYOUT_PHOTO_FOLDER, WATERMARK_PHOTO_FOLDER,
                     HUMAN_MATTING_FOLDER, HUMAN_MATTING_PATH)
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

# 向核心服务端发请求
def send_request(server_path: str, files, data, base64_in_response: str, save_path: str, params = None):
    # 参数检查
    if not server_path:
        logger.error("No request URL")
        raise ValueError("No request URL")
    elif not files:
        logger.error("No files")
        raise ValueError("No files")
    elif not data:
        logger.error("No data")
        raise ValueError("No data")
    elif not base64_in_response:
        logger.error("No base64_in_response")
        raise ValueError("No base64_in_response")
    elif not save_path:
        logger.error("No save path")
        raise ValueError("No save path")

    # 发送请求
    response = None
    if params is None:
        try:
            response = requests.post(server_path, files=files, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in request: {e}")
            raise
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise
    else:
        try:
            response = requests.post(server_path, params=params, files=files, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in request: {e}")
            raise
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise

    response_json = response.json()

    # 检查response_json中是否有特定字段
    if base64_in_response not in response_json:
        logger.error(f"No {base64_in_response} in JSON response")
        raise ValueError(f"No {base64_in_response} in JSON response")

    # 将base64数据转换为图片存储在本地
    image_path = None
    try:
        image_path = base64_to_image(response_json[base64_in_response], save_path)
    except KeyError as e:
        logger.error(f"Missing key in JSON response: {e}")
        raise
    except (base64.binascii.Error, IOError) as e:
        logger.error(f"Error in decoding image: {e}")
        raise

    return response_json, image_path


# 获取RGB颜色代码
def get_color_code(color_name: str):
    # 参数检查
    if not color_name:
        logger.error("No color name")
        raise ValueError("No color name")

    return color_dict.get(color_name, None)


# 将base64数据转换为图片
def base64_to_image(base64_data, generate_path: str):
    # 参数检查
    if not base64_data:
        logger.error("No base64 data")
        raise ValueError("No base64 data")
    elif len(generate_path) == 0:
        logger.error("No generate path")
        raise ValueError("No generate path")

    head, context = base64_data.split(",")
    try:
        image_data = base64.b64decode(context)
    except (base64.binascii.Error, ValueError) as e:
        logger.error(f"Error decoding base64 data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{current_time}.jpg"

    try:
        out_put_path = os.path.join(generate_path, file_name)
        out_put_path = os.path.normpath(out_put_path)  # 标准化路径
        with open(out_put_path, "wb") as f:
            f.write(image_data)
        return out_put_path
    except IOError as e:
        logger.error(f"Error saving image: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


# 为图片添加背景颜色
def add_background_color(input_image_path: str, color: str):
    # 参数检查
    if not input_image_path:
        logger.error("No input image path")
        raise ValueError("No input image path")
    elif not color:
        logger.error("No color")
        raise ValueError("No color")

    save_path = WITH_BACKGROUND_FOLDER
    base64_in_response = "image_base64"
    server_path = ADD_BACKGROUND_COLOR_PATH
    files = {"input_image": open(input_image_path, "rb")}
    data = {
        "color": get_color_code(color),
        "kb": None,
        "render": 0,
        "dpi": 300,
    }

    # 发送请求
    response_json = None
    image_path = None
    try:
        response_json, image_path = send_request(server_path, files, data, base64_in_response, save_path)
    except Exception as e:
        logger.error(f"Error in send request: {e}")
        raise

    # 检查返回数据是否为空
    if not response_json:
        logger.error("No response JSON")
        raise ValueError("No response JSON")
    elif not image_path:
        logger.error("No image path")
        raise ValueError("No image path")

    return response_json, image_path


# 生成透明底的证件照
def generate_id_photo(input_image_path: str):
    # 参数检查
    if not input_image_path:
        logger.error("No input image path")
        raise ValueError("No input image path")

    # 设置参数
    save_path = NONE_BACKGROUND_FOLDER
    base64_in_response = "image_base64_standard"
    server_path = ID_PHOTO_PATH
    params = {
        "head_measure_ratio": 0.2,
        "head_height_ratio": 0.45,
        "top_distance_max": 0.12,
        "top_distance_min": 0.1,
    }
    files = {"input_image": open(input_image_path, "rb")}
    data = {
        "height": 413,
        "width": 295,
        "human_matting_model": "modnet_photographic_portrait_matting",
        "face_detect_model": "mtcnn",
        "hd": True,
        "dpi": 300,
        "face_alignment": True,
    }

    response_json = None
    image_path = None
    try:
        response_json, image_path = send_request(server_path, files, data, base64_in_response, save_path, params)
    except Exception as e:
        logger.error(f"Error in send request: {e}")
        raise

    # 检查返回数据是否为空
    if not response_json:
        logger.error("No response JSON")
        raise ValueError("No response JSON")
    elif not image_path:
        logger.error("No image path")
        raise ValueError("No image path")

    return response_json, image_path


# 生成6寸排版照
def generate_layout_photo(input_image_path: str):
    # 参数检查
    if not input_image_path:
        logger.error("No input image path")
        raise ValueError("No input image path")

    save_path = LAYOUT_PHOTO_FOLDER
    base64_in_response = "image_base64"
    server_path = LAYOUT_PHOTO_PATH
    files = {"input_image": open(input_image_path, "rb")}
    data = {
        "height": 413,
        "width": 295,
        "kb": 200,
        "dpi": 300,
    }

    response_json = None
    image_path = None
    try:
        response_json, image_path = send_request(server_path, files, data, base64_in_response, save_path)
    except Exception as e:
        logger.error(f"Error in send request: {e}")
        raise

    # 检查返回数据是否为空
    if not response_json:
        logger.error("No response JSON")
        raise ValueError("No response JSON")
    elif not image_path:
        logger.error("No image path")
        raise ValueError("No image path")

    return response_json, image_path


# 为图片添加水印
def add_watermark(input_image_path: str, watermark_text: str):
    # 参数检查
    if not input_image_path:
        logger.error("No input image path")
        raise ValueError("No input image path")
    elif not watermark_text:
        logger.error("No watermark text")
        raise ValueError("No watermark text")

    save_path = WATERMARK_PHOTO_FOLDER
    base64_in_response = "image_base64"
    server_path = WATERMARK_PATH
    params = {
        "size": 20,
        "opacity": 0.27,
        "angle": 30,
        "color": "#808080",
        "space": 100,
    }
    files = {"input_image": open(input_image_path, "rb")}
    data = {"text": watermark_text, "dpi": 300}

    response_json = None
    image_path = None
    try:
        response_json, image_path = send_request(server_path, files, data, base64_in_response, save_path, params)
    except Exception as e:
        logger.error(f"Error in send request: {e}")
        raise

    # 检查返回数据是否为空
    if not response_json:
        logger.error("No response JSON")
        raise ValueError("No response JSON")
    elif not image_path:
        logger.error("No image path")
        raise ValueError("No image path")

    return response_json, image_path


def human_matting(input_image_path: str):
    # 参数检查
    if not input_image_path:
        logger.error("No input image path")
        raise ValueError("No input image path")

    save_path = HUMAN_MATTING_FOLDER
    base64_in_response = "image_base64"
    server_path = HUMAN_MATTING_PATH
    files = {"input_image": open(input_image_path, "rb")}
    data = {
        "human_matting_model": "modnet_photographic_portrait_matting",
        "dpi": 300,
    }

    response_json = None
    image_path = None
    try:
        response_json, image_path = send_request(server_path, files, data, base64_in_response, save_path)
    except Exception as e:
        logger.error(f"Error in send request: {e}")
        raise

    # 检查返回数据是否为空
    if not response_json:
        logger.error("No response JSON")
        raise ValueError("No response JSON")
    elif not image_path:
        logger.error("No image path")
        raise ValueError("No image path")

    return response_json, image_path