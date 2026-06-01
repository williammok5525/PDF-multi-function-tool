"""
工具函数
"""
import os
from typing import Callable

class Language:
    """多语言支持"""
    
    TEXTS = {
        'zh': {
            # 主窗口
            'app_title': 'PDF多功能处理工具',
            'language': '语言',
            
            # 标签页
            'tab_basic': '基础操作',
            'tab_convert': '格式转换',
            'tab_content': '内容处理',
            
            # 基础操作
            'merge_pdf': '合并PDF',
            'split_pdf': '拆分PDF',
            'rotate_pdf': '旋转页面',
            'delete_pages': '删除页面',
            'reorder_pages': '重排页面',
            'encrypt_pdf': '加密PDF',
            'decrypt_pdf': '解密PDF',
            'add_watermark': '添加水印',
            
            # 格式转换
            'pdf_to_image': 'PDF转图片',
            'image_to_pdf': '图片转PDF',
            'pdf_to_word': 'PDF转Word',
            'pdf_to_excel': 'PDF转Excel',
            'pdf_to_text': 'PDF转文本',
            'word_to_pdf': 'Word转PDF',
            'excel_to_pdf': 'Excel转PDF',
            'text_to_pdf': '文本转PDF',
            
            # 内容处理
            'extract_text': '提取文本',
            'extract_images': '提取图片',
            'extract_tables': '提取表格',
            'add_page_numbers': '添加页码',
            'add_bookmarks': '添加书签',
            'ocr_recognition': 'OCR识别',
            'compress_pdf': '压缩PDF',
            'pdf_info': 'PDF信息',
            
            # 按钮
            'select_file': '选择文件',
            'select_files': '选择文件',
            'select_folder': '选择文件夹',
            'add_file': '添加文件',
            'remove_file': '移除文件',
            'clear_list': '清空列表',
            'start_process': '开始处理',
            'cancel': '取消',
            'confirm': '确定',
            
            # 输入框标签
            'input_file': '输入文件:',
            'output_file': '输出文件:',
            'output_folder': '输出文件夹:',
            'file_list': '文件列表:',
            'start_page': '起始页:',
            'end_page': '结束页:',
            'password': '密码:',
            'watermark_text': '水印文字:',
            'opacity': '透明度:',
            'dpi': 'DPI:',
            'image_format': '图片格式:',
            'compression_level': '压缩级别:',
            'page_position': '页码位置:',
            
            # 提示信息
            'success': '成功',
            'error': '错误',
            'warning': '警告',
            'info': '信息',
            'processing': '处理中...',
            'completed': '处理完成！',
            'failed': '处理失败',
            'select_file_first': '请先选择文件',
            'select_output_path': '请选择输出路径',
            'invalid_input': '输入无效',
            
            # 位置选项
            'position_bottom_center': '底部居中',
            'position_bottom_left': '底部左侧',
            'position_bottom_right': '底部右侧',
            'position_top_center': '顶部居中',
            'position_top_left': '顶部左侧',
            'position_top_right': '顶部右侧',
            'position_center': '居中',
        },
        'en': {
            # Main Window
            'app_title': 'PDF Multi-function Tool',
            'language': 'Language',
            
            # Tabs
            'tab_basic': 'Basic Operations',
            'tab_convert': 'Format Conversion',
            'tab_content': 'Content Processing',
            
            # Basic Operations
            'merge_pdf': 'Merge PDF',
            'split_pdf': 'Split PDF',
            'rotate_pdf': 'Rotate Pages',
            'delete_pages': 'Delete Pages',
            'reorder_pages': 'Reorder Pages',
            'encrypt_pdf': 'Encrypt PDF',
            'decrypt_pdf': 'Decrypt PDF',
            'add_watermark': 'Add Watermark',
            
            # Format Conversion
            'pdf_to_image': 'PDF to Image',
            'image_to_pdf': 'Image to PDF',
            'pdf_to_word': 'PDF to Word',
            'pdf_to_excel': 'PDF to Excel',
            'pdf_to_text': 'PDF to Text',
            'word_to_pdf': 'Word to PDF',
            'excel_to_pdf': 'Excel to PDF',
            'text_to_pdf': 'Text to PDF',
            
            # Content Processing
            'extract_text': 'Extract Text',
            'extract_images': 'Extract Images',
            'extract_tables': 'Extract Tables',
            'add_page_numbers': 'Add Page Numbers',
            'add_bookmarks': 'Add Bookmarks',
            'ocr_recognition': 'OCR Recognition',
            'compress_pdf': 'Compress PDF',
            'pdf_info': 'PDF Info',
            
            # Buttons
            'select_file': 'Select File',
            'select_files': 'Select Files',
            'select_folder': 'Select Folder',
            'add_file': 'Add File',
            'remove_file': 'Remove File',
            'clear_list': 'Clear List',
            'start_process': 'Start Process',
            'cancel': 'Cancel',
            'confirm': 'Confirm',
            
            # Input Labels
            'input_file': 'Input File:',
            'output_file': 'Output File:',
            'output_folder': 'Output Folder:',
            'file_list': 'File List:',
            'start_page': 'Start Page:',
            'end_page': 'End Page:',
            'password': 'Password:',
            'watermark_text': 'Watermark Text:',
            'opacity': 'Opacity:',
            'dpi': 'DPI:',
            'image_format': 'Image Format:',
            'compression_level': 'Compression Level:',
            'page_position': 'Page Position:',
            
            # Messages
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'processing': 'Processing...',
            'completed': 'Process Completed!',
            'failed': 'Process Failed',
            'select_file_first': 'Please select a file first',
            'select_output_path': 'Please select output path',
            'invalid_input': 'Invalid input',
            
            # Position Options
            'position_bottom_center': 'Bottom Center',
            'position_bottom_left': 'Bottom Left',
            'position_bottom_right': 'Bottom Right',
            'position_top_center': 'Top Center',
            'position_top_left': 'Top Left',
            'position_top_right': 'Top Right',
            'position_center': 'Center',
        }
    }
    
    def __init__(self):
        self.current_language = 'zh'
    
    def get_text(self, key: str) -> str:
        """获取文本"""
        return self.TEXTS.get(self.current_language, {}).get(key, key)
    
    def set_language(self, lang: str):
        """设置语言"""
        if lang in self.TEXTS:
            self.current_language = lang
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.current_language


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    import re
    # 移除不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename