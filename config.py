"""
配置文件
"""
import os
import sys

class Config:
    """应用配置"""
    
    # 应用信息
    APP_NAME = "PDF多功能处理工具"
    APP_VERSION = "1.0.0"
    
    # 支持的文件格式
    SUPPORTED_PDF = [("PDF文件", "*.pdf")]
    SUPPORTED_IMAGES = [
        ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
        ("PNG文件", "*.png"),
        ("JPG文件", "*.jpg *.jpeg"),
        ("所有文件", "*.*")
    ]
    SUPPORTED_OFFICE = [
        ("Word文件", "*.docx *.doc"),
        ("Excel文件", "*.xlsx *.xls"),
        ("所有文件", "*.*")
    ]
    
    # 默认设置
    DEFAULT_DPI = 200
    DEFAULT_IMAGE_FORMAT = "PNG"
    DEFAULT_COMPRESSION_LEVEL = 3
    
    # OCR设置（需要安装Tesseract）
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_LANGUAGES = ['chi_sim', 'eng']  # 简体中文和英文
    
    @staticmethod
    def resource_path(relative_path):
        """获取资源文件的绝对路径（支持打包后运行）"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)