import sys
import os
import logging
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from pathlib import Path

from src.ui.main_window import MainWindow
from src.core.config_manager import ConfigManager

def get_app_data_dir() -> str:
    """获取应用数据目录"""
    if os.name == 'nt':  # Windows
        app_data = os.path.join(os.environ['APPDATA'], 'PipManager')
    else:  # Linux/Mac
        app_data = os.path.join(os.path.expanduser('~'), '.pipmanager')
    return app_data

def setup_logging():
    """配置日志"""
    try:
        # 获取应用数据目录
        app_data = get_app_data_dir()
        
        # 创建日志目录
        log_dir = os.path.join(app_data, 'logs')
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
    except Exception as e:
        # 如果日志设置失败，尝试使用基本配置
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("PipManager")
        logger.error(f"设置日志时出错: {str(e)}")
        return logger

def initialize_config(logger) -> ConfigManager:
    """初始化配置文件"""
    try:
        # 获取应用数据目录
        app_data = get_app_data_dir()
        config_dir = os.path.join(app_data, 'config')
        os.makedirs(config_dir, exist_ok=True)
        logger.info(f"创建配置目录: {config_dir}")
        
        # 初始化配置管理器
        config_manager = ConfigManager(config_dir)
        
        # 默认配置
        configs = {
            "settings": {
                "window": {
                    "width": 800,
                    "height": 600,
                    "maximized": False,
                    "position": {
                        "x": 100,
                        "y": 100
                    }
                },
                "general": {
                    "language": "zh_CN",
                    "auto_update": True,
                    "check_update_on_startup": True,
                    "save_window_state": True,
                    "show_notifications": True,
                    "notification_duration": 5000
                },
                "package": {
                    "auto_check_updates": True,
                    "show_package_details": True,
                    "confirm_uninstall": True,
                    "save_requirements_path": ""
                }
            },
            "proxy": {
                "enabled": False,
                "type": "HTTP",
                "host": "",
                "port": 1080,
                "auth_enabled": False,
                "username": "",
                "password": ""
            },
            "mirror": {
                "current": "清华大学",
                "mirrors": {
                    "清华大学": "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "阿里云": "https://mirrors.aliyun.com/pypi/simple",
                    "华为云": "https://repo.huaweicloud.com/repository/pypi/simple",
                    "中国科技大学": "https://pypi.mirrors.ustc.edu.cn/simple",
                    "豆瓣": "https://pypi.doubanio.com/simple"
                }
            },
            "theme": {
                "name": "浅色",
                "colors": {
                    "primary": "#1976D2",
                    "secondary": "#424242",
                    "background": "#FFFFFF",
                    "text": "#000000",
                    "error": "#FF5252",
                    "warning": "#FFC107",
                    "success": "#4CAF50"
                },
                "fonts": {
                    "family": "Microsoft YaHei",
                    "size": 12
                }
            }
        }
        
        # 创建默认配置
        for name, config in configs.items():
            if not config_manager.config_exists(name):
                logger.info(f"创建默认配置文件: {name}")
                if config_manager.save_config(name, config):
                    logger.info(f"默认配置文件 {name} 创建成功")
                else:
                    logger.error(f"创建默认配置文件 {name} 失败")
        
        return config_manager
    except Exception as e:
        logger.error(f"初始化配置时出错: {str(e)}")
        raise

def show_error_message(title: str, message: str):
    """显示错误消息对话框"""
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
    except:
        # 如果连错误对话框都无法显示，则打印到控制台
        print(f"错误: {title}\n{message}")

def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("应用启动")
    
    try:
        # 初始化Qt应用
        app = QApplication(sys.argv)
        
        # 初始化配置
        config_manager = initialize_config(logger)
        
        # 创建并显示主窗口
        window = MainWindow(config_manager)
        window.show()
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"应用运行时出错: {traceback.format_exc()}")
        QMessageBox.critical(None, "错误", f"应用启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 