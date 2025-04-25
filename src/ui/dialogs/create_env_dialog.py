from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class CreateEnvDialog(QDialog):
    """创建环境对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建环境")
        self.setMinimumWidth(400)
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 环境名称
        name_layout = QHBoxLayout()
        name_label = QLabel("环境名称:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 环境备注
        desc_layout = QHBoxLayout()
        desc_label = QLabel("环境备注:")
        self.desc_input = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # 环境路径
        path_layout = QHBoxLayout()
        path_label = QLabel("环境路径:")
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def browse_path(self):
        """浏览环境路径"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择环境目录"
        )
        if dir_path:
            self.path_input.setText(dir_path)
            
    def get_env_info(self):
        """获取环境信息"""
        return {
            'name': self.name_input.text().strip(),
            'description': self.desc_input.text().strip(),
            'path': self.path_input.text().strip()
        }
        
    def validate(self):
        """验证输入"""
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "错误", "请输入环境名称")
            return False
            
        if not path:
            QMessageBox.warning(self, "错误", "请选择环境路径")
            return False
            
        return True
        
    def accept(self):
        """确认创建"""
        if self.validate():
            super().accept() 