from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class InstallPackageDialog(QDialog):
    """安装包对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("安装包")
        self.setMinimumWidth(400)
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 包名
        name_layout = QHBoxLayout()
        name_label = QLabel("包名:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 版本
        version_layout = QHBoxLayout()
        version_label = QLabel("版本:")
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("可选，例如: 1.0.0")
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_input)
        layout.addLayout(version_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        install_btn = QPushButton("安装")
        install_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(install_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def get_package_info(self):
        """获取包信息"""
        name = self.name_input.text().strip()
        version = self.version_input.text().strip()
        
        if version:
            name = f"{name}=={version}"
            
        return name
        
    def validate(self):
        """验证输入"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "错误", "请输入包名")
            return False
            
        return True
        
    def accept(self):
        """确认安装"""
        if self.validate():
            super().accept() 