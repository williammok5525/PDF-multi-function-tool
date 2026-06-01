import sys
from PyQt5.QtWidgets import QApplication
from gui import PDFToolMainWindow  # 简化的导入

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 设置应用程序信息
    app.setApplicationName("PDF多功能处理工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("YourCompany")
    
    # 创建主窗口
    window = PDFToolMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()