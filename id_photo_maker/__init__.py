# __init__.py

import os
import logging
from .functions import generate_id_photo, add_background_color, generate_layout_photo, add_watermark, human_matting
from .config import (UPLOAD_FOLDER, NONE_BACKGROUND_FOLDER, WITH_BACKGROUND_FOLDER,
                     LAYOUT_PHOTO_FOLDER, WATERMARK_PHOTO_FOLDER, HUMAN_MATTING_FOLDER, AHEAD, NO_HUMAN_FACE)

__all__ = [
    'generate_id_photo',
    'add_background_color',
    'generate_layout_photo',
    'add_watermark',
    'UPLOAD_FOLDER',
    'human_matting',
    'AHEAD',
    'NO_HUMAN_FACE'
]

# 创建目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(NONE_BACKGROUND_FOLDER, exist_ok=True)
os.makedirs(WITH_BACKGROUND_FOLDER, exist_ok=True)
os.makedirs(LAYOUT_PHOTO_FOLDER, exist_ok=True)
os.makedirs(WATERMARK_PHOTO_FOLDER, exist_ok=True)
os.makedirs(HUMAN_MATTING_FOLDER, exist_ok=True)

# 配置日志记录
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

