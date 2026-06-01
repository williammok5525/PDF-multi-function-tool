"""
PDF内容处理功能
包括：文本提取、图片提取、表格提取、添加页码、添加书签、OCR识别、压缩
"""

import fitz
import pdfplumber
from PIL import Image
import pytesseract
import io
import os
from typing import List, Dict
from config import Config

class ContentProcessor:
    """内容处理类"""
    
    @staticmethod
    def extract_text(input_path: str, page_range: tuple = None) -> Dict[int, str]:
        """
        提取文本
        
        Args:
            page_range: (start, end) 页码范围，None表示全部
        
        Returns:
            {页码: 文本内容}
        """
        try:
            doc = fitz.open(input_path)
            result = {}
            
            start = page_range[0] - 1 if page_range else 0
            end = page_range[1] if page_range else len(doc)
            
            for page_num in range(start, end):
                page = doc[page_num]
                text = page.get_text()
                result[page_num + 1] = text
            
            doc.close()
            return result
        except Exception as e:
            raise Exception(f"提取文本失败: {str(e)}")
    
    @staticmethod
    def extract_images(input_path: str, output_folder: str,
                      progress_callback=None) -> List[str]:
        """
        提取PDF中的所有图片
        
        Returns:
            保存的图片路径列表
        """
        try:
            os.makedirs(output_folder, exist_ok=True)
            doc = fitz.open(input_path)
            
            image_list = []
            image_count = 0
            total = len(doc)
            
            for page_num in range(total):
                page = doc[page_num]
                images = page.get_images()
                
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 保存图片
                    image_count += 1
                    image_filename = os.path.join(
                        output_folder,
                        f"image_{page_num + 1}_{img_index + 1}.{image_ext}"
                    )
                    
                    with open(image_filename, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    image_list.append(image_filename)
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            doc.close()
            return image_list
        except Exception as e:
            raise Exception(f"提取图片失败: {str(e)}")
    
    @staticmethod
    def extract_tables(input_path: str, output_folder: str,
                      format: str = 'csv', progress_callback=None) -> List[str]:
        """
        提取表格
        
        Args:
            format: 输出格式 'csv' 或 'excel'
        
        Returns:
            保存的表格文件路径列表
        """
        try:
            os.makedirs(output_folder, exist_ok=True)
            output_files = []
            
            with pdfplumber.open(input_path) as pdf:
                total = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if format == 'csv':
                            import csv
                            output_file = os.path.join(
                                output_folder,
                                f"table_page{page_num + 1}_{table_idx + 1}.csv"
                            )
                            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerows(table)
                        else:  # excel
                            from openpyxl import Workbook
                            output_file = os.path.join(
                                output_folder,
                                f"table_page{page_num + 1}_{table_idx + 1}.xlsx"
                            )
                            wb = Workbook()
                            ws = wb.active
                            for row in table:
                                ws.append(row)
                            wb.save(output_file)
                        
                        output_files.append(output_file)
                    
                    if progress_callback:
                        progress_callback(int((page_num + 1) / total * 100))
            
            return output_files
        except Exception as e:
            raise Exception(f"提取表格失败: {str(e)}")
    
    @staticmethod
    def add_page_numbers(input_path: str, output_path: str,
                        position: str = 'bottom-center',
                        start_number: int = 1,
                        font_size: int = 12,
                        progress_callback=None) -> bool:
        """
        添加页码
        
        Args:
            position: 位置 'bottom-center', 'bottom-left', 'bottom-right',
                     'top-center', 'top-left', 'top-right'
            start_number: 起始页码
        """
        try:
            doc = fitz.open(input_path)
            total = len(doc)
            
            for page_num in range(total):
                page = doc[page_num]
                rect = page.rect
                
                # 计算位置
                if 'bottom' in position:
                    y = rect.height - 30
                else:  # top
                    y = 30
                
                if 'center' in position:
                    x = rect.width / 2
                    align = fitz.TEXT_ALIGN_CENTER
                elif 'left' in position:
                    x = 30
                    align = fitz.TEXT_ALIGN_LEFT
                else:  # right
                    x = rect.width - 30
                    align = fitz.TEXT_ALIGN_RIGHT
                
                # 插入页码
                text = str(start_number + page_num)
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=font_size,
                    color=(0, 0, 0),
                    align=align
                )
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            raise Exception(f"添加页码失败: {str(e)}")
    
    @staticmethod
    def add_bookmarks(input_path: str, output_path: str,
                     bookmarks: List[Dict], progress_callback=None) -> bool:
        """
        添加书签/目录
        
        Args:
            bookmarks: 书签列表，格式：
                [
                    {'title': '第一章', 'page': 1, 'level': 1},
                    {'title': '1.1节', 'page': 2, 'level': 2},
                ]
        """
        try:
            doc = fitz.open(input_path)
            
            # 删除现有目录
            doc.set_toc([])
            
            # 构建目录结构
            toc = []
            for bookmark in bookmarks:
                toc.append([
                    bookmark['level'],
                    bookmark['title'],
                    bookmark['page']
                ])
            
            # 设置新目录
            doc.set_toc(toc)
            
            doc.save(output_path)
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            return True
        except Exception as e:
            raise Exception(f"添加书签失败: {str(e)}")
    
    @staticmethod
    def ocr_pdf(input_path: str, output_path: str,
               language: str = 'chi_sim+eng',
               progress_callback=None) -> bool:
        """
        OCR识别（将扫描版PDF转为可搜索PDF）
        
        Args:
            language: OCR语言，'chi_sim'=简体中文, 'eng'=英文
        
        注意：需要安装Tesseract-OCR
        """
        try:
            # 设置Tesseract路径
            if os.path.exists(Config.TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
            
            doc = fitz.open(input_path)
            total = len(doc)
            
            for page_num in range(total):
                page = doc[page_num]
                
                # 将页面转为图片
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # OCR识别
                text = pytesseract.image_to_string(img, lang=language)
                
                # 在页面上添加不可见的文本层
                # 这样PDF既保持原样，又可以搜索和复制文字
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total * 100))
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}\n请确保已安装Tesseract-OCR")
    
    @staticmethod
    def ocr_image_pdf(input_path: str, output_path: str,
                     language: str = 'chi_sim+eng') -> str:
        """
        OCR识别并提取文本（仅返回文本，不生成PDF）
        """
        try:
            if os.path.exists(Config.TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
            
            doc = fitz.open(input_path)
            all_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                text = pytesseract.image_to_string(img, lang=language)
                all_text.append(f"=== 第 {page_num + 1} 页 ===\n{text}\n")
            
            doc.close()
            
            # 保存文本
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
            
            return '\n'.join(all_text)
        except Exception as e:
            raise Exception(f"OCR文本提取失败: {str(e)}")
    
    @staticmethod
    def compress_pdf(input_path: str, output_path: str,
                    compression_level: int = 3,
                    progress_callback=None) -> bool:
        """
        压缩PDF
        
        Args:
            compression_level: 压缩级别 0-4
                0: 不压缩
                1: 轻度压缩
                2: 中度压缩
                3: 高度压缩
                4: 极限压缩
        """
        try:
            doc = fitz.open(input_path)
            
            # 压缩设置
            if compression_level == 0:
                doc.save(output_path)
            elif compression_level == 1:
                doc.save(output_path, garbage=1, deflate=True)
            elif compression_level == 2:
                doc.save(output_path, garbage=2, deflate=True)
            elif compression_level == 3:
                doc.save(output_path, garbage=3, deflate=True, clean=True)
            else:  # 4
                doc.save(output_path, garbage=4, deflate=True, 
                        clean=True, linear=True)
            
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            # 计算压缩率
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100
            
            return True
        except Exception as e:
            raise Exception(f"压缩失败: {str(e)}")
    
    @staticmethod
    def get_pdf_info(input_path: str) -> Dict:
        """
        获取PDF文件信息
        """
        try:
            doc = fitz.open(input_path)
            
            info = {
                'pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'keywords': doc.metadata.get('keywords', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'mod_date': doc.metadata.get('modDate', ''),
                'file_size': os.path.getsize(input_path),
                'encrypted': doc.is_encrypted,
            }
            
            doc.close()
            return info
        except Exception as e:
            raise Exception(f"获取信息失败: {str(e)}")