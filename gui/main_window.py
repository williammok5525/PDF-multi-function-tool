"""
主窗口GUI实现
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QLineEdit, 
    QFileDialog, QMessageBox, QProgressBar, QListWidget,
    QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QGridLayout, QTextEdit, QRadioButton, QButtonGroup,
    QCheckBox, QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.basic_ops import BasicOperations
from core.converter import FormatConverter
from core.content_proc import ContentProcessor
from utils.helpers import Language, format_file_size
from config import Config


class WorkerThread(QThread):
    """工作线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs, 
                             progress_callback=self.update_progress)
            self.finished.emit(True, str(result))
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def update_progress(self, value):
        self.progress.emit(value)


class PDFToolMainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.lang = Language()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(self.lang.get_text('app_title'))
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个功能标签页
        self.create_basic_tab()
        self.create_convert_tab()
        self.create_content_tab()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 状态栏
        self.statusBar().showMessage('就绪' if self.lang.current_language == 'zh' else 'Ready')
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 语言菜单
        lang_menu = menubar.addMenu(self.lang.get_text('language'))
        
        # 中文选项
        zh_action = QAction('中文', self)
        zh_action.triggered.connect(lambda: self.switch_language('zh'))
        lang_menu.addAction(zh_action)
        
        # 英文选项
        en_action = QAction('English', self)
        en_action.triggered.connect(lambda: self.switch_language('en'))
        lang_menu.addAction(en_action)
    
    def switch_language(self, lang: str):
        """切換語言"""
        self.lang.set_language(lang)
    
        # 保存當前選項卡索引
        current_index = self.tab_widget.currentIndex()
    
        # 清除並重新創建所有選項卡
        self.tab_widget.clear()
        self.create_basic_tab()
        self.create_convert_tab()
        self.create_content_tab()
    
        # 恢復選項卡索引
        self.tab_widget.setCurrentIndex(current_index)
    
        # 更新狀態欄和標題
        self.statusBar().showMessage('Ready' if lang == 'en' else '就绪')
        self.setWindowTitle(self.lang.get_text('app_title'))
    
    # ==================== 基础操作标签页 ====================
    
    def create_basic_tab(self):
        """创建基础操作标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 创建按钮组
        buttons_layout = QGridLayout()
        
        # 合并PDF
        merge_btn = QPushButton(self.lang.get_text('merge_pdf'))
        merge_btn.clicked.connect(self.show_merge_dialog)
        buttons_layout.addWidget(merge_btn, 0, 0)
        
        # 拆分PDF
        split_btn = QPushButton(self.lang.get_text('split_pdf'))
        split_btn.clicked.connect(self.show_split_dialog)
        buttons_layout.addWidget(split_btn, 0, 1)
        
        # 旋转页面
        rotate_btn = QPushButton(self.lang.get_text('rotate_pdf'))
        rotate_btn.clicked.connect(self.show_rotate_dialog)
        buttons_layout.addWidget(rotate_btn, 0, 2)
        
        # 删除页面
        delete_btn = QPushButton(self.lang.get_text('delete_pages'))
        delete_btn.clicked.connect(self.show_delete_dialog)
        buttons_layout.addWidget(delete_btn, 1, 0)
        
        # 重排页面
        reorder_btn = QPushButton(self.lang.get_text('reorder_pages'))
        reorder_btn.clicked.connect(self.show_reorder_dialog)
        buttons_layout.addWidget(reorder_btn, 1, 1)
        
        # 加密PDF
        encrypt_btn = QPushButton(self.lang.get_text('encrypt_pdf'))
        encrypt_btn.clicked.connect(self.show_encrypt_dialog)
        buttons_layout.addWidget(encrypt_btn, 1, 2)
        
        # 解密PDF
        decrypt_btn = QPushButton(self.lang.get_text('decrypt_pdf'))
        decrypt_btn.clicked.connect(self.show_decrypt_dialog)
        buttons_layout.addWidget(decrypt_btn, 2, 0)
        
        # 添加水印
        watermark_btn = QPushButton(self.lang.get_text('add_watermark'))
        watermark_btn.clicked.connect(self.show_watermark_dialog)
        buttons_layout.addWidget(watermark_btn, 2, 1)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, self.lang.get_text('tab_basic'))
    
    def show_merge_dialog(self):
        """显示合并PDF对话框"""
        dialog = MergePDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_split_dialog(self):
        """显示拆分PDF对话框"""
        dialog = SplitPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_rotate_dialog(self):
        """显示旋转页面对话框"""
        dialog = RotatePDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_delete_dialog(self):
        """显示删除页面对话框"""
        dialog = DeletePagesDialog(self, self.lang)
        dialog.exec_()
    
    def show_reorder_dialog(self):
        """显示重排页面对话框"""
        dialog = ReorderPagesDialog(self, self.lang)
        dialog.exec_()
    
    def show_encrypt_dialog(self):
        """显示加密对话框"""
        dialog = EncryptPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_decrypt_dialog(self):
        """显示解密对话框"""
        dialog = DecryptPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_watermark_dialog(self):
        """显示添加水印对话框"""
        dialog = WatermarkDialog(self, self.lang)
        dialog.exec_()
    
    # ==================== 格式转换标签页 ====================
    
    def create_convert_tab(self):
        """创建格式转换标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 创建按钮组
        buttons_layout = QGridLayout()
        
        # PDF转图片
        pdf_to_img_btn = QPushButton(self.lang.get_text('pdf_to_image'))
        pdf_to_img_btn.clicked.connect(self.show_pdf_to_image_dialog)
        buttons_layout.addWidget(pdf_to_img_btn, 0, 0)
        
        # 图片转PDF
        img_to_pdf_btn = QPushButton(self.lang.get_text('image_to_pdf'))
        img_to_pdf_btn.clicked.connect(self.show_image_to_pdf_dialog)
        buttons_layout.addWidget(img_to_pdf_btn, 0, 1)
        
        # PDF转Word
        pdf_to_word_btn = QPushButton(self.lang.get_text('pdf_to_word'))
        pdf_to_word_btn.clicked.connect(self.show_pdf_to_word_dialog)
        buttons_layout.addWidget(pdf_to_word_btn, 0, 2)
        
        # PDF转Excel
        pdf_to_excel_btn = QPushButton(self.lang.get_text('pdf_to_excel'))
        pdf_to_excel_btn.clicked.connect(self.show_pdf_to_excel_dialog)
        buttons_layout.addWidget(pdf_to_excel_btn, 1, 0)
        
        # PDF转文本
        pdf_to_text_btn = QPushButton(self.lang.get_text('pdf_to_text'))
        pdf_to_text_btn.clicked.connect(self.show_pdf_to_text_dialog)
        buttons_layout.addWidget(pdf_to_text_btn, 1, 1)
        
        # Word转PDF
        word_to_pdf_btn = QPushButton(self.lang.get_text('word_to_pdf'))
        word_to_pdf_btn.clicked.connect(self.show_word_to_pdf_dialog)
        buttons_layout.addWidget(word_to_pdf_btn, 1, 2)
        
        # 文本转PDF
        text_to_pdf_btn = QPushButton(self.lang.get_text('text_to_pdf'))
        text_to_pdf_btn.clicked.connect(self.show_text_to_pdf_dialog)
        buttons_layout.addWidget(text_to_pdf_btn, 2, 0)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, self.lang.get_text('tab_convert'))
    
    def show_pdf_to_image_dialog(self):
        """显示PDF转图片对话框"""
        dialog = PDFToImageDialog(self, self.lang)
        dialog.exec_()
    
    def show_image_to_pdf_dialog(self):
        """显示图片转PDF对话框"""
        dialog = ImageToPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_pdf_to_word_dialog(self):
        """显示PDF转Word对话框"""
        dialog = PDFToWordDialog(self, self.lang)
        dialog.exec_()
    
    def show_pdf_to_excel_dialog(self):
        """显示PDF转Excel对话框"""
        dialog = PDFToExcelDialog(self, self.lang)
        dialog.exec_()
    
    def show_pdf_to_text_dialog(self):
        """显示PDF转文本对话框"""
        dialog = PDFToTextDialog(self, self.lang)
        dialog.exec_()
    
    def show_word_to_pdf_dialog(self):
        """显示Word转PDF对话框"""
        dialog = WordToPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_text_to_pdf_dialog(self):
        """显示文本转PDF对话框"""
        dialog = TextToPDFDialog(self, self.lang)
        dialog.exec_()
    
    # ==================== 内容处理标签页 ====================
    
    def create_content_tab(self):
        """创建内容处理标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 创建按钮组
        buttons_layout = QGridLayout()
        
        # 提取文本
        extract_text_btn = QPushButton(self.lang.get_text('extract_text'))
        extract_text_btn.clicked.connect(self.show_extract_text_dialog)
        buttons_layout.addWidget(extract_text_btn, 0, 0)
        
        # 提取图片
        extract_img_btn = QPushButton(self.lang.get_text('extract_images'))
        extract_img_btn.clicked.connect(self.show_extract_images_dialog)
        buttons_layout.addWidget(extract_img_btn, 0, 1)
        
        # 提取表格
        extract_table_btn = QPushButton(self.lang.get_text('extract_tables'))
        extract_table_btn.clicked.connect(self.show_extract_tables_dialog)
        buttons_layout.addWidget(extract_table_btn, 0, 2)
        
        # 添加页码
        add_page_num_btn = QPushButton(self.lang.get_text('add_page_numbers'))
        add_page_num_btn.clicked.connect(self.show_add_page_numbers_dialog)
        buttons_layout.addWidget(add_page_num_btn, 1, 0)
        
        # 添加书签
        add_bookmark_btn = QPushButton(self.lang.get_text('add_bookmarks'))
        add_bookmark_btn.clicked.connect(self.show_add_bookmarks_dialog)
        buttons_layout.addWidget(add_bookmark_btn, 1, 1)
        
        # OCR识别
        ocr_btn = QPushButton(self.lang.get_text('ocr_recognition'))
        ocr_btn.clicked.connect(self.show_ocr_dialog)
        buttons_layout.addWidget(ocr_btn, 1, 2)
        
        # 压缩PDF
        compress_btn = QPushButton(self.lang.get_text('compress_pdf'))
        compress_btn.clicked.connect(self.show_compress_dialog)
        buttons_layout.addWidget(compress_btn, 2, 0)
        
        # PDF信息
        info_btn = QPushButton(self.lang.get_text('pdf_info'))
        info_btn.clicked.connect(self.show_pdf_info_dialog)
        buttons_layout.addWidget(info_btn, 2, 1)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, self.lang.get_text('tab_content'))
    
    def show_extract_text_dialog(self):
        """显示提取文本对话框"""
        dialog = ExtractTextDialog(self, self.lang)
        dialog.exec_()
    
    def show_extract_images_dialog(self):
        """显示提取图片对话框"""
        dialog = ExtractImagesDialog(self, self.lang)
        dialog.exec_()
    
    def show_extract_tables_dialog(self):
        """显示提取表格对话框"""
        dialog = ExtractTablesDialog(self, self.lang)
        dialog.exec_()
    
    def show_add_page_numbers_dialog(self):
        """显示添加页码对话框"""
        dialog = AddPageNumbersDialog(self, self.lang)
        dialog.exec_()
    
    def show_add_bookmarks_dialog(self):
        """显示添加书签对话框"""
        dialog = AddBookmarksDialog(self, self.lang)
        dialog.exec_()
    
    def show_ocr_dialog(self):
        """显示OCR识别对话框"""
        dialog = OCRDialog(self, self.lang)
        dialog.exec_()
    
    def show_compress_dialog(self):
        """显示压缩对话框"""
        dialog = CompressPDFDialog(self, self.lang)
        dialog.exec_()
    
    def show_pdf_info_dialog(self):
        """显示PDF信息对话框"""
        dialog = PDFInfoDialog(self, self.lang)
        dialog.exec_()


# ==================== 对话框类 ====================

from PyQt5.QtWidgets import QDialog

class MergePDFDialog(QDialog):
    """合并PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.pdf_files = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('merge_pdf'))
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 文件列表
        list_label = QLabel(self.lang.get_text('file_list'))
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(self.lang.get_text('add_file'))
        add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton(self.lang.get_text('remove_file'))
        remove_btn.clicked.connect(self.remove_file)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton(self.lang.get_text('clear_list'))
        clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.merge_pdfs)
        layout.addWidget(start_btn)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.lang.get_text('select_files'),
            "",
            "PDF Files (*.pdf)"
        )
        for file in files:
            if file not in self.pdf_files:
                self.pdf_files.append(file)
                self.file_list.addItem(os.path.basename(file))
    
    def remove_file(self):
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            self.file_list.takeItem(current_row)
            self.pdf_files.pop(current_row)
    
    def clear_list(self):
        self.file_list.clear()
        self.pdf_files.clear()
    
    def merge_pdfs(self):
        if len(self.pdf_files) < 2:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                "Please select at least 2 PDF files" if self.lang.current_language == 'en' 
                else "请至少选择2个PDF文件"
            )
            return
        
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        
        if output_file:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            self.worker = WorkerThread(
                BasicOperations.merge_pdfs,
                self.pdf_files,
                output_file
            )
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class SplitPDFDialog(QDialog):
    """拆分PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('split_pdf'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 分割方式
        split_group = QGroupBox("Split Method" if self.lang.current_language == 'en' else "分割方式")
        split_layout = QVBoxLayout()
        
        self.split_type = QButtonGroup()
        
        self.by_range_radio = QRadioButton("By Page Range" if self.lang.current_language == 'en' else "按页码范围")
        self.by_range_radio.setChecked(True)
        self.split_type.addButton(self.by_range_radio, 1)
        split_layout.addWidget(self.by_range_radio)
        
        # 页码范围输入
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel(self.lang.get_text('start_page')))
        self.start_page = QSpinBox()
        self.start_page.setMinimum(1)
        self.start_page.setValue(1)
        range_layout.addWidget(self.start_page)
        
        range_layout.addWidget(QLabel(self.lang.get_text('end_page')))
        self.end_page = QSpinBox()
        self.end_page.setMinimum(1)
        self.end_page.setValue(1)
        range_layout.addWidget(self.end_page)
        split_layout.addLayout(range_layout)
        
        self.by_page_radio = QRadioButton("Each Page" if self.lang.current_language == 'en' else "每页独立")
        self.split_type.addButton(self.by_page_radio, 2)
        split_layout.addWidget(self.by_page_radio)
        
        split_group.setLayout(split_layout)
        layout.addWidget(split_group)
        
        # 输出文件夹
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_folder'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_folder'))
        output_btn.clicked.connect(self.select_output_folder)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.split_pdf)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang.get_text('select_folder')
        )
        if folder:
            self.output_edit.setText(folder)
    
    def split_pdf(self):
        if not self.input_file:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        if not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_output_path')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        output_folder = self.output_edit.text()
        
        if self.by_range_radio.isChecked():
            # 按范围拆分
            ranges = [(self.start_page.value(), self.end_page.value())]
            self.worker = WorkerThread(
                BasicOperations.split_pdf,
                self.input_file,
                ranges,
                output_folder
            )
        else:
            # 按页拆分
            self.worker = WorkerThread(
                BasicOperations.split_by_page,
                self.input_file,
                output_folder
            )
        
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class RotatePDFDialog(QDialog):
    """旋转PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('rotate_pdf'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 旋转设置
        rotate_group = QGroupBox("Rotation Settings" if self.lang.current_language == 'en' else "旋转设置")
        rotate_layout = QVBoxLayout()
        
        # 页码范围
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Pages:" if self.lang.current_language == 'en' else "页码:"))
        self.pages_edit = QLineEdit()
        self.pages_edit.setPlaceholderText("e.g., 1,3,5-7" if self.lang.current_language == 'en' else "例如: 1,3,5-7")
        page_layout.addWidget(self.pages_edit)
        rotate_layout.addLayout(page_layout)
        
        # 旋转角度
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Angle:" if self.lang.current_language == 'en' else "角度:"))
        self.angle_combo = QComboBox()
        self.angle_combo.addItems(['90°', '180°', '270°'])
        angle_layout.addWidget(self.angle_combo)
        angle_layout.addStretch()
        rotate_layout.addLayout(angle_layout)
        
        rotate_group.setLayout(rotate_layout)
        layout.addWidget(rotate_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.rotate_pdf)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def parse_pages(self, pages_str):
        """解析页码字符串 例如: "1,3,5-7" -> {1, 3, 5, 6, 7}"""
        pages = set()
        for part in pages_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.update(range(start, end + 1))
            else:
                pages.add(int(part))
        return pages
    
    def rotate_pdf(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            pages = self.parse_pages(self.pages_edit.text())
            angle = int(self.angle_combo.currentText().replace('°', ''))
            
            page_rotations = {page: angle for page in pages}
            
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            self.worker = WorkerThread(
                BasicOperations.rotate_pages,
                self.input_file,
                self.output_edit.text(),
                page_rotations
            )
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )

# 继续其他对话框...

# 继续 gui/main_window.py

class DeletePagesDialog(QDialog):
    """删除页面对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('delete_pages'))
        self.setGeometry(200, 200, 500, 250)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 要删除的页码
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Pages to delete:" if self.lang.current_language == 'en' else "要删除的页码:"))
        self.pages_edit = QLineEdit()
        self.pages_edit.setPlaceholderText("e.g., 1,3,5-7" if self.lang.current_language == 'en' else "例如: 1,3,5-7")
        pages_layout.addWidget(self.pages_edit)
        layout.addLayout(pages_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.delete_pages)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def parse_pages(self, pages_str):
        """解析页码字符串"""
        pages = []
        for part in pages_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
        return pages
    
    def delete_pages(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            pages_to_delete = self.parse_pages(self.pages_edit.text())
            
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            self.worker = WorkerThread(
                BasicOperations.delete_pages,
                self.input_file,
                self.output_edit.text(),
                pages_to_delete
            )
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class ReorderPagesDialog(QDialog):
    """重排页面对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('reorder_pages'))
        self.setGeometry(200, 200, 500, 250)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 新顺序
        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("New order:" if self.lang.current_language == 'en' else "新顺序:"))
        self.order_edit = QLineEdit()
        self.order_edit.setPlaceholderText("e.g., 3,1,2,4" if self.lang.current_language == 'en' else "例如: 3,1,2,4")
        order_layout.addWidget(self.order_edit)
        layout.addLayout(order_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.reorder_pages)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def reorder_pages(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            new_order = [int(x.strip()) for x in self.order_edit.text().split(',')]
            
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            self.worker = WorkerThread(
                BasicOperations.reorder_pages,
                self.input_file,
                self.output_edit.text(),
                new_order
            )
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class EncryptPDFDialog(QDialog):
    """加密PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('encrypt_pdf'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 密码设置
        password_group = QGroupBox("Password Settings" if self.lang.current_language == 'en' else "密码设置")
        password_layout = QVBoxLayout()
        
        # 用户密码
        user_pwd_layout = QHBoxLayout()
        user_pwd_layout.addWidget(QLabel("User Password:" if self.lang.current_language == 'en' else "用户密码:"))
        self.user_pwd_edit = QLineEdit()
        self.user_pwd_edit.setEchoMode(QLineEdit.Password)
        user_pwd_layout.addWidget(self.user_pwd_edit)
        password_layout.addLayout(user_pwd_layout)
        
        # 所有者密码
        owner_pwd_layout = QHBoxLayout()
        owner_pwd_layout.addWidget(QLabel("Owner Password:" if self.lang.current_language == 'en' else "所有者密码:"))
        self.owner_pwd_edit = QLineEdit()
        self.owner_pwd_edit.setEchoMode(QLineEdit.Password)
        owner_pwd_layout.addWidget(self.owner_pwd_edit)
        password_layout.addLayout(owner_pwd_layout)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.encrypt_pdf)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def encrypt_pdf(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        if not self.user_pwd_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                "Please enter password" if self.lang.current_language == 'en' else "请输入密码"
            )
            return
        
        try:
            BasicOperations.encrypt_pdf(
                self.input_file,
                self.output_edit.text(),
                self.user_pwd_edit.text(),
                self.owner_pwd_edit.text() or None
            )
            
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )


class DecryptPDFDialog(QDialog):
    """解密PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('decrypt_pdf'))
        self.setGeometry(200, 200, 500, 250)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 密码
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel(self.lang.get_text('password')))
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        pwd_layout.addWidget(self.pwd_edit)
        layout.addLayout(pwd_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.decrypt_pdf)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def decrypt_pdf(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            BasicOperations.decrypt_pdf(
                self.input_file,
                self.output_edit.text(),
                self.pwd_edit.text()
            )
            
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )


class WatermarkDialog(QDialog):
    """添加水印对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('add_watermark'))
        self.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 水印类型
        watermark_group = QGroupBox("Watermark Settings" if self.lang.current_language == 'en' else "水印设置")
        watermark_layout = QVBoxLayout()
        
        # 类型选择
        type_layout = QHBoxLayout()
        self.text_radio = QRadioButton("Text Watermark" if self.lang.current_language == 'en' else "文字水印")
        self.text_radio.setChecked(True)
        self.text_radio.toggled.connect(self.on_type_changed)
        self.image_radio = QRadioButton("Image Watermark" if self.lang.current_language == 'en' else "图片水印")
        type_layout.addWidget(self.text_radio)
        type_layout.addWidget(self.image_radio)
        watermark_layout.addLayout(type_layout)
        
        # 文字水印输入
        self.text_input_layout = QHBoxLayout()
        self.text_input_layout.addWidget(QLabel(self.lang.get_text('watermark_text')))
        self.watermark_text_edit = QLineEdit()
        self.watermark_text_edit.setPlaceholderText("Watermark" if self.lang.current_language == 'en' else "水印")
        self.text_input_layout.addWidget(self.watermark_text_edit)
        watermark_layout.addLayout(self.text_input_layout)
        
        # 图片水印选择
        self.image_input_layout = QHBoxLayout()
        self.image_input_layout.addWidget(QLabel("Image:" if self.lang.current_language == 'en' else "图片:"))
        self.watermark_image_edit = QLineEdit()
        self.watermark_image_edit.setReadOnly(True)
        self.image_input_layout.addWidget(self.watermark_image_edit)
        image_btn = QPushButton(self.lang.get_text('select_file'))
        image_btn.clicked.connect(self.select_watermark_image)
        self.image_input_layout.addWidget(image_btn)
        watermark_layout.addLayout(self.image_input_layout)
        self.image_input_layout.setEnabled(False)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel(self.lang.get_text('opacity')))
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.setValue(0.3)
        opacity_layout.addWidget(self.opacity_spin)
        opacity_layout.addStretch()
        watermark_layout.addLayout(opacity_layout)
        
        # 位置
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:" if self.lang.current_language == 'en' else "位置:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            self.lang.get_text('position_center'),
            self.lang.get_text('position_top_left'),
            self.lang.get_text('position_top_right'),
            self.lang.get_text('position_bottom_left'),
            self.lang.get_text('position_bottom_right'),
        ])
        position_layout.addWidget(self.position_combo)
        position_layout.addStretch()
        watermark_layout.addLayout(position_layout)
        
        watermark_group.setLayout(watermark_layout)
        layout.addWidget(watermark_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.add_watermark)
        layout.addWidget(start_btn)
    
    def on_type_changed(self):
        is_text = self.text_radio.isChecked()
        self.text_input_layout.setEnabled(is_text)
        self.image_input_layout.setEnabled(not is_text)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_watermark_image(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file:
            self.watermark_image_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def add_watermark(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # 位置映射
        position_map = {
            0: 'center',
            1: 'top-left',
            2: 'top-right',
            3: 'bottom-left',
            4: 'bottom-right'
        }
        position = position_map[self.position_combo.currentIndex()]
        
        try:
            if self.text_radio.isChecked():
                # 文字水印
                self.worker = WorkerThread(
                    BasicOperations.add_text_watermark,
                    self.input_file,
                    self.output_edit.text(),
                    self.watermark_text_edit.text(),
                    self.opacity_spin.value()
                )
            else:
                # 图片水印
                if not self.watermark_image_edit.text():
                    QMessageBox.warning(
                        self,
                        self.lang.get_text('warning'),
                        "Please select watermark image" if self.lang.current_language == 'en' else "请选择水印图片"
                    )
                    self.progress.setVisible(False)
                    return
                
                self.worker = WorkerThread(
                    BasicOperations.add_image_watermark,
                    self.input_file,
                    self.output_edit.text(),
                    self.watermark_image_edit.text(),
                    self.opacity_spin.value(),
                    position
                )
            
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


# ==================== 格式转换对话框 ====================

class PDFToImageDialog(QDialog):
    """PDF转图片对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('pdf_to_image'))
        self.setGeometry(200, 200, 500, 350)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 设置组
        settings_group = QGroupBox("Settings" if self.lang.current_language == 'en' else "设置")
        settings_layout = QVBoxLayout()
        
        # 图片格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self.lang.get_text('image_format')))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG', 'JPG', 'BMP', 'TIFF'])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        settings_layout.addLayout(format_layout)
        
        # DPI
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel(self.lang.get_text('dpi')))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(200)
        self.dpi_spin.setSingleStep(50)
        dpi_layout.addWidget(self.dpi_spin)
        dpi_layout.addStretch()
        settings_layout.addLayout(dpi_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 输出文件夹
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_folder'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_folder'))
        output_btn.clicked.connect(self.select_output_folder)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang.get_text('select_folder')
        )
        if folder:
            self.output_edit.setText(folder)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            FormatConverter.pdf_to_images,
            self.input_file,
            self.output_edit.text(),
            self.format_combo.currentText(),
            self.dpi_spin.value()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class ImageToPDFDialog(QDialog):
    """图片转PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.image_files = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('image_to_pdf'))
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 文件列表
        list_label = QLabel(self.lang.get_text('file_list'))
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(self.lang.get_text('add_file'))
        add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton(self.lang.get_text('remove_file'))
        remove_btn.clicked.connect(self.remove_file)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton(self.lang.get_text('clear_list'))
        clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.lang.get_text('select_files'),
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_list.addItem(os.path.basename(file))
    
    def remove_file(self):
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            self.file_list.takeItem(current_row)
            self.image_files.pop(current_row)
    
    def clear_list(self):
        self.file_list.clear()
        self.image_files.clear()
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.image_files:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                "Please select at least one image" if self.lang.current_language == 'en' else "请至少选择一张图片"
            )
            return
        
        if not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_output_path')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            FormatConverter.images_to_pdf,
            self.image_files,
            self.output_edit.text()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class PDFToWordDialog(QDialog):
    """PDF转Word对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('pdf_to_word'))
        self.setGeometry(200, 200, 500, 200)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "Word Files (*.docx)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            FormatConverter.pdf_to_word,
            self.input_file,
            self.output_edit.text()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class PDFToExcelDialog(QDialog):
    """PDF转Excel对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('pdf_to_excel'))
        self.setGeometry(200, 200, 500, 200)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "Excel Files (*.xlsx)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            FormatConverter.pdf_to_excel,
            self.input_file,
            self.output_edit.text()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class PDFToTextDialog(QDialog):
    """PDF转文本对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('pdf_to_text'))
        self.setGeometry(200, 200, 500, 200)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "Text Files (*.txt)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            FormatConverter.pdf_to_text,
            self.input_file,
            self.output_edit.text()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class WordToPDFDialog(QDialog):
    """Word转PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('word_to_pdf'))
        self.setGeometry(200, 200, 500, 200)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 提示信息
        hint_label = QLabel("Note: Requires Microsoft Word or LibreOffice" if self.lang.current_language == 'en' 
                           else "注意：需要安装 Microsoft Word 或 LibreOffice")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(hint_label)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "Word Files (*.docx *.doc)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            FormatConverter.word_to_pdf(
                self.input_file,
                self.output_edit.text()
            )
            
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )


class TextToPDFDialog(QDialog):
    """文本转PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('text_to_pdf'))
        self.setGeometry(200, 200, 500, 200)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.convert)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "Text Files (*.txt)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def convert(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            FormatConverter.text_to_pdf(
                self.input_file,
                self.output_edit.text()
            )
            
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )

# 继续 gui/main_window.py - 内容处理对话框

class ExtractTextDialog(QDialog):
    """提取文本对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('extract_text'))
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 页码范围
        range_layout = QHBoxLayout()
        self.all_pages_check = QCheckBox("All Pages" if self.lang.current_language == 'en' else "所有页面")
        self.all_pages_check.setChecked(True)
        self.all_pages_check.toggled.connect(self.on_all_pages_toggled)
        range_layout.addWidget(self.all_pages_check)
        
        range_layout.addWidget(QLabel(self.lang.get_text('start_page')))
        self.start_page = QSpinBox()
        self.start_page.setMinimum(1)
        self.start_page.setEnabled(False)
        range_layout.addWidget(self.start_page)
        
        range_layout.addWidget(QLabel(self.lang.get_text('end_page')))
        self.end_page = QSpinBox()
        self.end_page.setMinimum(1)
        self.end_page.setEnabled(False)
        range_layout.addWidget(self.end_page)
        
        range_layout.addStretch()
        layout.addLayout(range_layout)
        
        # 提取按钮
        extract_btn = QPushButton("Extract" if self.lang.current_language == 'en' else "提取")
        extract_btn.clicked.connect(self.extract_text)
        layout.addWidget(extract_btn)
        
        # 文本显示区域
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)
        
        # 保存按钮
        save_btn = QPushButton("Save to File" if self.lang.current_language == 'en' else "保存到文件")
        save_btn.clicked.connect(self.save_to_file)
        layout.addWidget(save_btn)
    
    def on_all_pages_toggled(self, checked):
        self.start_page.setEnabled(not checked)
        self.end_page.setEnabled(not checked)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def extract_text(self):
        if not self.input_file:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            page_range = None if self.all_pages_check.isChecked() else \
                        (self.start_page.value(), self.end_page.value())
            
            text_dict = ContentProcessor.extract_text(self.input_file, page_range)
            
            # 显示文本
            all_text = []
            for page_num, text in text_dict.items():
                all_text.append(f"{'='*50}\n第 {page_num} 页 / Page {page_num}\n{'='*50}\n{text}\n")
            
            self.text_display.setPlainText('\n'.join(all_text))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
    
    def save_to_file(self):
        if not self.text_display.toPlainText():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                "No text to save" if self.lang.current_language == 'en' else "没有可保存的文本"
            )
            return
        
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "Text Files (*.txt)"
        )
        
        if file:
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(self.text_display.toPlainText())
                
                QMessageBox.information(
                    self,
                    self.lang.get_text('success'),
                    self.lang.get_text('completed')
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.lang.get_text('error'),
                    str(e)
                )


class ExtractImagesDialog(QDialog):
    """提取图片对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('extract_images'))
        self.setGeometry(200, 200, 500, 250)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出文件夹
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_folder'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_folder'))
        output_btn.clicked.connect(self.select_output_folder)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.extract_images)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang.get_text('select_folder')
        )
        if folder:
            self.output_edit.setText(folder)
    
    def extract_images(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            ContentProcessor.extract_images,
            self.input_file,
            self.output_edit.text()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            # message包含提取的图片列表
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                f"{self.lang.get_text('completed')}\n{'提取了' if self.lang.current_language == 'zh' else 'Extracted'} {len(eval(message))} {'张图片' if self.lang.current_language == 'zh' else 'images'}"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class ExtractTablesDialog(QDialog):
    """提取表格对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('extract_tables'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:" if self.lang.current_language == 'en' else "输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['CSV', 'Excel'])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # 输出文件夹
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_folder'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_folder'))
        output_btn.clicked.connect(self.select_output_folder)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.extract_tables)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang.get_text('select_folder')
        )
        if folder:
            self.output_edit.setText(folder)
    
    def extract_tables(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        format_type = 'csv' if self.format_combo.currentIndex() == 0 else 'excel'
        
        self.worker = WorkerThread(
            ContentProcessor.extract_tables,
            self.input_file,
            self.output_edit.text(),
            format_type
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class AddPageNumbersDialog(QDialog):
    """添加页码对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('add_page_numbers'))
        self.setGeometry(200, 200, 500, 350)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 页码设置
        settings_group = QGroupBox("Page Number Settings" if self.lang.current_language == 'en' else "页码设置")
        settings_layout = QVBoxLayout()
        
        # 位置
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel(self.lang.get_text('page_position')))
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            self.lang.get_text('position_bottom_center'),
            self.lang.get_text('position_bottom_left'),
            self.lang.get_text('position_bottom_right'),
            self.lang.get_text('position_top_center'),
            self.lang.get_text('position_top_left'),
            self.lang.get_text('position_top_right'),
        ])
        position_layout.addWidget(self.position_combo)
        position_layout.addStretch()
        settings_layout.addLayout(position_layout)
        
        # 起始页码
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Number:" if self.lang.current_language == 'en' else "起始页码:"))
        self.start_number = QSpinBox()
        self.start_number.setMinimum(1)
        self.start_number.setValue(1)
        start_layout.addWidget(self.start_number)
        start_layout.addStretch()
        settings_layout.addLayout(start_layout)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:" if self.lang.current_language == 'en' else "字体大小:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        settings_layout.addLayout(font_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.add_page_numbers)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def add_page_numbers(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        # 位置映射
        position_map = {
            0: 'bottom-center',
            1: 'bottom-left',
            2: 'bottom-right',
            3: 'top-center',
            4: 'top-left',
            5: 'top-right'
        }
        position = position_map[self.position_combo.currentIndex()]
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            ContentProcessor.add_page_numbers,
            self.input_file,
            self.output_edit.text(),
            position,
            self.start_number.value(),
            self.font_size.value()
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class AddBookmarksDialog(QDialog):
    """添加书签对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.bookmarks = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('add_bookmarks'))
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 书签列表
        bookmark_group = QGroupBox("Bookmarks" if self.lang.current_language == 'en' else "书签列表")
        bookmark_layout = QVBoxLayout()
        
        self.bookmark_list = QListWidget()
        bookmark_layout.addWidget(self.bookmark_list)
        
        # 添加书签输入
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Title:" if self.lang.current_language == 'en' else "标题:"))
        self.title_edit = QLineEdit()
        add_layout.addWidget(self.title_edit)
        
        add_layout.addWidget(QLabel("Page:" if self.lang.current_language == 'en' else "页码:"))
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        add_layout.addWidget(self.page_spin)
        
        add_layout.addWidget(QLabel("Level:" if self.lang.current_language == 'en' else "级别:"))
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 3)
        self.level_spin.setValue(1)
        add_layout.addWidget(self.level_spin)
        
        add_bookmark_btn = QPushButton("Add" if self.lang.current_language == 'en' else "添加")
        add_bookmark_btn.clicked.connect(self.add_bookmark)
        add_layout.addWidget(add_bookmark_btn)
        
        bookmark_layout.addLayout(add_layout)
        
        # 移除按钮
        remove_btn = QPushButton("Remove Selected" if self.lang.current_language == 'en' else "移除选中")
        remove_btn.clicked.connect(self.remove_bookmark)
        bookmark_layout.addWidget(remove_btn)
        
        bookmark_group.setLayout(bookmark_layout)
        layout.addWidget(bookmark_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.add_bookmarks)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def add_bookmark(self):
        if not self.title_edit.text():
            return
        
        bookmark = {
            'title': self.title_edit.text(),
            'page': self.page_spin.value(),
            'level': self.level_spin.value()
        }
        self.bookmarks.append(bookmark)
        
        indent = '  ' * (bookmark['level'] - 1)
        self.bookmark_list.addItem(f"{indent}{bookmark['title']} - Page {bookmark['page']} (Level {bookmark['level']})")
        
        # 清空输入
        self.title_edit.clear()
        self.page_spin.setValue(self.page_spin.value() + 1)
    
    def remove_bookmark(self):
        current_row = self.bookmark_list.currentRow()
        if current_row >= 0:
            self.bookmark_list.takeItem(current_row)
            self.bookmarks.pop(current_row)
    
    def add_bookmarks(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        if not self.bookmarks:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                "Please add at least one bookmark" if self.lang.current_language == 'en' else "请至少添加一个书签"
            )
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            ContentProcessor.add_bookmarks,
            self.input_file,
            self.output_edit.text(),
            self.bookmarks
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class OCRDialog(QDialog):
    """OCR识别对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('ocr_recognition'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 提示信息
        hint_label = QLabel("Note: Requires Tesseract-OCR installed" if self.lang.current_language == 'en' 
                           else "注意：需要安装 Tesseract-OCR")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(hint_label)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # OCR设置
        settings_group = QGroupBox("OCR Settings" if self.lang.current_language == 'en' else "OCR设置")
        settings_layout = QVBoxLayout()
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:" if self.lang.current_language == 'en' else "语言:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            'Chinese + English (chi_sim+eng)',
            'English only (eng)',
            'Chinese only (chi_sim)'
        ])
        lang_layout.addWidget(self.lang_combo)
        settings_layout.addLayout(lang_layout)
        
        # 输出类型
        output_type_layout = QHBoxLayout()
        output_type_layout.addWidget(QLabel("Output Type:" if self.lang.current_language == 'en' else "输出类型:"))
        self.output_type_combo = QComboBox()
        self.output_type_combo.addItems([
            'Searchable PDF' if self.lang.current_language == 'en' else '可搜索PDF',
            'Text File Only' if self.lang.current_language == 'en' else '仅文本文件'
        ])
        output_type_layout.addWidget(self.output_type_combo)
        settings_layout.addLayout(output_type_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.perform_ocr)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def select_output_file(self):
        if self.output_type_combo.currentIndex() == 0:
            file_filter = "PDF Files (*.pdf)"
        else:
            file_filter = "Text Files (*.txt)"
        
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            file_filter
        )
        if file:
            self.output_edit.setText(file)
    
    def perform_ocr(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        # 语言映射
        lang_map = {
            0: 'chi_sim+eng',
            1: 'eng',
            2: 'chi_sim'
        }
        language = lang_map[self.lang_combo.currentIndex()]
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        if self.output_type_combo.currentIndex() == 0:
            # 可搜索PDF
            self.worker = WorkerThread(
                ContentProcessor.ocr_pdf,
                self.input_file,
                self.output_edit.text(),
                language
            )
        else:
            # 仅文本
            self.worker = WorkerThread(
                ContentProcessor.ocr_image_pdf,
                self.input_file,
                self.output_edit.text(),
                language
            )
        
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(
                self,
                self.lang.get_text('success'),
                self.lang.get_text('completed')
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class CompressPDFDialog(QDialog):
    """压缩PDF对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('compress_pdf'))
        self.setGeometry(200, 200, 500, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 文件大小显示
        self.size_label = QLabel("Original size: -" if self.lang.current_language == 'en' else "原始大小: -")
        layout.addWidget(self.size_label)
        
        # 压缩级别
        compress_group = QGroupBox("Compression Settings" if self.lang.current_language == 'en' else "压缩设置")
        compress_layout = QVBoxLayout()
        
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel(self.lang.get_text('compression_level')))
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            'Low (Fast)' if self.lang.current_language == 'en' else '低 (快速)',
            'Medium' if self.lang.current_language == 'en' else '中',
            'High' if self.lang.current_language == 'en' else '高',
            'Maximum' if self.lang.current_language == 'en' else '最大'
        ])
        self.level_combo.setCurrentIndex(2)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        compress_layout.addLayout(level_layout)
        
        compress_group.setLayout(compress_layout)
        layout.addWidget(compress_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_label = QLabel(self.lang.get_text('output_file'))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_btn = QPushButton(self.lang.get_text('select_file'))
        output_btn.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 开始按钮
        start_btn = QPushButton(self.lang.get_text('start_process'))
        start_btn.clicked.connect(self.compress_pdf)
        layout.addWidget(start_btn)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
            
            # 显示文件大小
            size = os.path.getsize(file)
            self.size_label.setText(
                f"{'Original size:' if self.lang.current_language == 'en' else '原始大小:'} {format_file_size(size)}"
            )
    
    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get_text('output_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)
    
    def compress_pdf(self):
        if not self.input_file or not self.output_edit.text():
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        compression_level = self.level_combo.currentIndex() + 1
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = WorkerThread(
            ContentProcessor.compress_pdf,
            self.input_file,
            self.output_edit.text(),
            compression_level
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            # 显示压缩后的大小
            if os.path.exists(self.output_edit.text()):
                original_size = os.path.getsize(self.input_file)
                compressed_size = os.path.getsize(self.output_edit.text())
                ratio = (1 - compressed_size / original_size) * 100
                
                QMessageBox.information(
                    self,
                    self.lang.get_text('success'),
                    f"{self.lang.get_text('completed')}\n"
                    f"{'Original:' if self.lang.current_language == 'en' else '原始大小:'} {format_file_size(original_size)}\n"
                    f"{'Compressed:' if self.lang.current_language == 'en' else '压缩后:'} {format_file_size(compressed_size)}\n"
                    f"{'Saved:' if self.lang.current_language == 'en' else '节省:'} {ratio:.1f}%"
                )
            else:
                QMessageBox.information(
                    self,
                    self.lang.get_text('success'),
                    self.lang.get_text('completed')
                )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                message
            )


class PDFInfoDialog(QDialog):
    """PDF信息对话框"""
    
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.input_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.lang.get_text('pdf_info'))
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get_text('input_file'))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_btn = QPushButton(self.lang.get_text('select_file'))
        input_btn.clicked.connect(self.select_input_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # 获取信息按钮
        get_info_btn = QPushButton("Get Information" if self.lang.current_language == 'en' else "获取信息")
        get_info_btn.clicked.connect(self.get_info)
        layout.addWidget(get_info_btn)
        
        # 信息显示区域
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        layout.addWidget(self.info_display)
    
    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get_text('select_file'),
            "",
            "PDF Files (*.pdf)"
        )
        if file:
            self.input_file = file
            self.input_edit.setText(file)
    
    def get_info(self):
        if not self.input_file:
            QMessageBox.warning(
                self,
                self.lang.get_text('warning'),
                self.lang.get_text('select_file_first')
            )
            return
        
        try:
            info = ContentProcessor.get_pdf_info(self.input_file)
            
            # 格式化显示信息
            info_text = []
            info_text.append("="*50)
            info_text.append("PDF INFORMATION" if self.lang.current_language == 'en' else "PDF 文件信息")
            info_text.append("="*50)
            info_text.append("")
            
            info_text.append(f"{'File Name:' if self.lang.current_language == 'en' else '文件名:'} {os.path.basename(self.input_file)}")
            info_text.append(f"{'File Size:' if self.lang.current_language == 'en' else '文件大小:'} {format_file_size(info['file_size'])}")
            info_text.append(f"{'Total Pages:' if self.lang.current_language == 'en' else '总页数:'} {info['pages']}")
            info_text.append(f"{'Encrypted:' if self.lang.current_language == 'en' else '是否加密:'} {'Yes' if info['encrypted'] else 'No'}")
            info_text.append("")
            
            info_text.append("="*50)
            info_text.append("METADATA" if self.lang.current_language == 'en' else "元数据")
            info_text.append("="*50)
            info_text.append("")
            
            info_text.append(f"{'Title:' if self.lang.current_language == 'en' else '标题:'} {info['title'] or 'N/A'}")
            info_text.append(f"{'Author:' if self.lang.current_language == 'en' else '作者:'} {info['author'] or 'N/A'}")
            info_text.append(f"{'Subject:' if self.lang.current_language == 'en' else '主题:'} {info['subject'] or 'N/A'}")
            info_text.append(f"{'Keywords:' if self.lang.current_language == 'en' else '关键词:'} {info['keywords'] or 'N/A'}")
            info_text.append(f"{'Creator:' if self.lang.current_language == 'en' else '创建者:'} {info['creator'] or 'N/A'}")
            info_text.append(f"{'Producer:' if self.lang.current_language == 'en' else '生成器:'} {info['producer'] or 'N/A'}")
            info_text.append(f"{'Creation Date:' if self.lang.current_language == 'en' else '创建日期:'} {info['creation_date'] or 'N/A'}")
            info_text.append(f"{'Modification Date:' if self.lang.current_language == 'en' else '修改日期:'} {info['mod_date'] or 'N/A'}")
            
            self.info_display.setPlainText('\n'.join(info_text))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang.get_text('error'),
                str(e)
            )
            