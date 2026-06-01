"""
PDF基础操作功能
包括：合并、拆分、旋转、删除、重排序、加密/解密、添加水印
"""

from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import fitz  # PyMuPDF
import os
from typing import List, Tuple

class BasicOperations:
    """PDF基础操作类"""
    
    @staticmethod
    def merge_pdfs(pdf_list: List[str], output_path: str, 
                   progress_callback=None) -> bool:
        """
        合并多个PDF文件
        
        Args:
            pdf_list: PDF文件路径列表
            output_path: 输出文件路径
            progress_callback: 进度回调函数
        """
        try:
            merger = PdfMerger()
            total = len(pdf_list)
            
            for idx, pdf in enumerate(pdf_list):
                merger.append(pdf)
                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            
            merger.write(output_path)
            merger.close()
            return True
        except Exception as e:
            raise Exception(f"合并PDF失败: {str(e)}")
    
    @staticmethod
    def split_pdf(input_path: str, ranges: List[Tuple[int, int]], 
                  output_folder: str, progress_callback=None) -> List[str]:
        """
        拆分PDF文件
        
        Args:
            input_path: 输入PDF路径
            ranges: 页码范围列表 [(1,3), (4,6)] 表示1-3页和4-6页
            output_folder: 输出文件夹
            progress_callback: 进度回调
        
        Returns:
            生成的文件路径列表
        """
        try:
            reader = PdfReader(input_path)
            os.makedirs(output_folder, exist_ok=True)
            
            output_files = []
            total = len(ranges)
            
            for idx, (start, end) in enumerate(ranges):
                writer = PdfWriter()
                
                # 页码从0开始
                for page_num in range(start - 1, end):
                    if page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
                
                output_file = os.path.join(
                    output_folder, 
                    f"split_{idx + 1}_page{start}-{end}.pdf"
                )
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                output_files.append(output_file)
                
                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            
            return output_files
        except Exception as e:
            raise Exception(f"拆分PDF失败: {str(e)}")
    
    @staticmethod
    def split_by_page(input_path: str, output_folder: str, 
                      progress_callback=None) -> List[str]:
        """
        按页拆分PDF（每页一个文件）
        """
        try:
            reader = PdfReader(input_path)
            os.makedirs(output_folder, exist_ok=True)
            
            output_files = []
            total = len(reader.pages)
            
            for page_num in range(total):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_file = os.path.join(
                    output_folder,
                    f"page_{page_num + 1}.pdf"
                )
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                output_files.append(output_file)
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            return output_files
        except Exception as e:
            raise Exception(f"按页拆分失败: {str(e)}")
    
    @staticmethod
    def rotate_pages(input_path: str, output_path: str, 
                     page_rotations: dict, progress_callback=None) -> bool:
        """
        旋转PDF页面
        
        Args:
            input_path: 输入文件
            output_path: 输出文件
            page_rotations: {页码: 旋转角度} 如 {1: 90, 2: 180}
                          页码从1开始，角度必须是90的倍数
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total = len(reader.pages)
            
            for page_num in range(total):
                page = reader.pages[page_num]
                
                # 如果该页需要旋转
                if page_num + 1 in page_rotations:
                    angle = page_rotations[page_num + 1]
                    page.rotate(angle)
                
                writer.add_page(page)
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            with open(output_path, 'wb') as output:
                writer.write(output)
            
            return True
        except Exception as e:
            raise Exception(f"旋转页面失败: {str(e)}")
    
    @staticmethod
    def delete_pages(input_path: str, output_path: str, 
                     pages_to_delete: List[int], progress_callback=None) -> bool:
        """
        删除指定页面
        
        Args:
            pages_to_delete: 要删除的页码列表（从1开始）
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total = len(reader.pages)
            pages_to_keep = set(range(1, total + 1)) - set(pages_to_delete)
            
            for page_num in sorted(pages_to_keep):
                writer.add_page(reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as output:
                writer.write(output)
            
            if progress_callback:
                progress_callback(100)
            
            return True
        except Exception as e:
            raise Exception(f"删除页面失败: {str(e)}")
    
    @staticmethod
    def reorder_pages(input_path: str, output_path: str, 
                      new_order: List[int], progress_callback=None) -> bool:
        """
        重新排序页面
        
        Args:
            new_order: 新的页面顺序 如 [3, 1, 2] 表示第3页放第一，第1页放第二...
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total = len(new_order)
            
            for idx, page_num in enumerate(new_order):
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                
                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            
            with open(output_path, 'wb') as output:
                writer.write(output)
            
            return True
        except Exception as e:
            raise Exception(f"重排序失败: {str(e)}")
    
    @staticmethod
    def encrypt_pdf(input_path: str, output_path: str, 
                    user_password: str, owner_password: str = None) -> bool:
        """
        加密PDF
        
        Args:
            user_password: 用户密码（打开文件需要）
            owner_password: 所有者密码（修改权限需要）
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # 加密
            writer.encrypt(
                user_password=user_password,
                owner_password=owner_password or user_password,
                algorithm="AES-256"
            )
            
            with open(output_path, 'wb') as output:
                writer.write(output)
            
            return True
        except Exception as e:
            raise Exception(f"加密失败: {str(e)}")
    
    @staticmethod
    def decrypt_pdf(input_path: str, output_path: str, 
                    password: str) -> bool:
        """解密PDF"""
        try:
            reader = PdfReader(input_path)
            
            if reader.is_encrypted:
                reader.decrypt(password)
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            with open(output_path, 'wb') as output:
                writer.write(output)
            
            return True
        except Exception as e:
            raise Exception(f"解密失败: {str(e)}")
    
    @staticmethod
    def add_text_watermark(input_path: str, output_path: str, 
                          watermark_text: str, opacity: float = 0.3,
                          font_size: int = 50, color: tuple = (0.5, 0.5, 0.5),
                          progress_callback=None) -> bool:
        """
        添加文字水印
        
        Args:
            watermark_text: 水印文字
            opacity: 透明度 0-1
            font_size: 字体大小
            color: RGB颜色 (0-1, 0-1, 0-1)
        """
        try:
            doc = fitz.open(input_path)
            total = len(doc)
            
            for page_num in range(total):
                page = doc[page_num]
                
                # 获取页面尺寸
                rect = page.rect
                
                # 在页面中心添加水印
                text_rect = fitz.Rect(
                    rect.width * 0.2, 
                    rect.height * 0.4,
                    rect.width * 0.8, 
                    rect.height * 0.6
                )
                
                # 插入文字
                page.insert_textbox(
                    text_rect,
                    watermark_text,
                    fontsize=font_size,
                    color=color,
                    rotate=45,  # 旋转45度
                    overlay=True,
                    opacity=opacity
                )
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            raise Exception(f"添加水印失败: {str(e)}")
    
    @staticmethod
    def add_image_watermark(input_path: str, output_path: str,
                           watermark_image: str, opacity: float = 0.3,
                           position: str = 'center', progress_callback=None) -> bool:
        """
        添加图片水印
        
        Args:
            watermark_image: 水印图片路径
            position: 位置 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        """
        try:
            doc = fitz.open(input_path)
            total = len(doc)
            
            for page_num in range(total):
                page = doc[page_num]
                rect = page.rect
                
                # 根据位置计算坐标
                img_rect = None
                if position == 'center':
                    img_rect = fitz.Rect(
                        rect.width * 0.3, rect.height * 0.3,
                        rect.width * 0.7, rect.height * 0.7
                    )
                elif position == 'top-left':
                    img_rect = fitz.Rect(10, 10, 110, 110)
                # 可以添加更多位置...
                
                if img_rect:
                    page.insert_image(img_rect, filename=watermark_image,
                                    overlay=True, opacity=opacity)
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            raise Exception(f"添加图片水印失败: {str(e)}")