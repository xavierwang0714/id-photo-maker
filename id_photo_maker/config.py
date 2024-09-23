# config.py

# 设置上传及生成文件的保存路径
UPLOAD_FOLDER = 'uploads'  # 上传文件保存路径
NONE_BACKGROUND_FOLDER = 'generate/none_background'  # 生成透明背景图片保存路径
WITH_BACKGROUND_FOLDER = 'generate/with_background'  # 生成有背景图片保存路径
LAYOUT_PHOTO_FOLDER = 'generate/layout_photo'
WATERMARK_PHOTO_FOLDER = 'generate/watermark'
HUMAN_MATTING_FOLDER = 'generate/human_matting'

# 定义请求路径
BASIC_PATH = "http://127.0.0.1:8080"
ID_PHOTO_PATH = BASIC_PATH + "/idphoto"
ADD_BACKGROUND_COLOR_PATH = BASIC_PATH + "/add_background"
LAYOUT_PHOTO_PATH = BASIC_PATH + "/generate_layout_photos"
HUMAN_MATTING_PATH = BASIC_PATH + "/human_matting"
WATERMARK_PATH = BASIC_PATH + "/watermark"

# 定义所有ahead字段
AHEAD = ["id-photo", "human-matting", "layout-photo", "watermark"]

# 定义颜色名称和对应的 RGB 颜色代码
color_dict = {
    "red": 'EB3324',
    "blue": '7BD6EB',
    "white": 'FFFFFF',
    "pink": 'EB9BE2',
}

# 定义特定错误
NO_HUMAN_FACE = "No image_base64_standard in JSON response"

