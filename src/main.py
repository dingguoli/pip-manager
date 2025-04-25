import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.ui.main_window import MainWindow

def setup_logging():
    """配置日志"""
    # 获取应用目录
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建日志目录
    log_dir = os.path.join(app_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志
    log_file = os.path.join(log_dir, f"pip_manager_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("PipManager")

def main():
    """主函数"""
    # 配置日志
    logger = setup_logging()
    logger.info("启动应用")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 