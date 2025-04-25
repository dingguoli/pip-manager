from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                            QPushButton, QListWidget, QListWidgetItem,
                            QLabel, QColorDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ThemeDialog(QDialog):
    """主题设置对话框"""
    
    # 预定义主题
    PREDEFINED_THEMES = {
        "浅色": {
            "background": "#FFFFFF",
            "text": "#000000",
            "primary": "#1976D2",
            "secondary": "#424242",
            "success": "#4CAF50",
            "warning": "#FFC107",
            "error": "#F44336"
        },
        "深色": {
            "background": "#121212",
            "text": "#FFFFFF",
            "primary": "#90CAF9",
            "secondary": "#B0BEC5",
            "success": "#81C784",
            "warning": "#FFD54F",
            "error": "#E57373"
        },
        "护眼": {
            "background": "#C7EDCC",
            "text": "#2C3E50",
            "primary": "#27AE60",
            "secondary": "#7F8C8D",
            "success": "#2ECC71",
            "warning": "#F1C40F",
            "error": "#E74C3C"
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.current_theme = {}
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 左侧预设主题列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("预设主题:"))
        
        self.theme_list = QListWidget()
        for theme_name in self.PREDEFINED_THEMES:
            item = QListWidgetItem(theme_name)
            self.theme_list.addItem(item)
        self.theme_list.currentItemChanged.connect(self.on_theme_selected)
        left_layout.addWidget(self.theme_list)
        
        layout.addLayout(left_layout)
        
        # 右侧颜色设置
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("自定义颜色:"))
        
        form_layout = QFormLayout()
        self.color_buttons = {}
        
        for color_name, display_name in [
            ("background", "背景色"),
            ("text", "文本色"),
            ("primary", "主要色"),
            ("secondary", "次要色"),
            ("success", "成功色"),
            ("warning", "警告色"),
            ("error", "错误色")
        ]:
            btn = QPushButton()
            btn.setFixedSize(100, 30)
            btn.clicked.connect(lambda checked, name=color_name: self.choose_color(name))
            self.color_buttons[color_name] = btn
            form_layout.addRow(f"{display_name}:", btn)
            
        right_layout.addLayout(form_layout)
        
        # 预览区域
        preview = QLabel("预览效果")
        preview.setAlignment(Qt.AlignCenter)
        preview.setStyleSheet("background-color: #F0F0F0; padding: 10px;")
        right_layout.addWidget(preview)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        right_layout.addLayout(btn_layout)
        
        layout.addLayout(right_layout)
        
    def on_theme_selected(self, current, previous):
        """主题选择变更处理"""
        if not current:
            return
            
        theme_name = current.text()
        if theme_name in self.PREDEFINED_THEMES:
            self.current_theme = self.PREDEFINED_THEMES[theme_name].copy()
            self.update_color_buttons()
            
    def choose_color(self, color_name: str):
        """选择颜色"""
        current_color = QColor(self.current_theme.get(color_name, "#000000"))
        color = QColorDialog.getColor(current_color, self, f"选择{color_name}颜色")
        
        if color.isValid():
            self.current_theme[color_name] = color.name()
            self.update_color_buttons()
            
    def update_color_buttons(self):
        """更新颜色按钮显示"""
        for name, btn in self.color_buttons.items():
            color = self.current_theme.get(name, "#000000")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #CCCCCC;
                }}
            """)
            
    def get_theme_config(self) -> dict:
        """获取主题配置"""
        return self.current_theme.copy()
        
    def set_theme_config(self, config: dict):
        """设置主题配置"""
        self.current_theme = config.copy()
        self.update_color_buttons()
        
        # 查找匹配的预定义主题
        for theme_name, theme_colors in self.PREDEFINED_THEMES.items():
            if theme_colors == config:
                # 选中对应的列表项
                items = self.theme_list.findItems(theme_name, Qt.MatchExactly)
                if items:
                    self.theme_list.setCurrentItem(items[0]) 