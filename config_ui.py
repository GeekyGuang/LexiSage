from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

# 笔记类型配置类 - 用于存储单个笔记类型的配置
class NoteTypeConfig:
    def __init__(self, note_type="", field_to_explain="", context_field="", destination_field=""):
        self.note_type = note_type
        self.field_to_explain = field_to_explain
        self.context_field = context_field
        self.destination_field = destination_field

# 配置对话框
class ConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # 直接使用"anki_lexisage"作为插件ID
        self.config = mw.addonManager.getConfig("anki_lexisage")
        if not self.config:
            self.config = {}

        # 初始化笔记类型配置列表
        self.note_type_configs = []
        self.load_note_type_configs()

        self.setupUI()

    def load_note_type_configs(self):
        # 兼容旧版配置格式
        if "noteTypeConfigs" in self.config:
            # 新格式：多笔记类型配置
            configs = self.config.get("noteTypeConfigs", {})
            for note_type, config_data in configs.items():
                self.note_type_configs.append(NoteTypeConfig(
                    note_type=note_type,
                    field_to_explain=config_data.get("fieldToExplain", ""),
                    context_field=config_data.get("contextField", ""),
                    destination_field=config_data.get("destinationField", "")
                ))
        elif "selectedNoteType" in self.config:
            # 旧格式：单笔记类型配置
            note_type = self.config.get("selectedNoteType", "")
            if note_type:
                self.note_type_configs.append(NoteTypeConfig(
                    note_type=note_type,
                    field_to_explain=self.config.get("fieldToExplain", ""),
                    context_field=self.config.get("contextField", ""),
                    destination_field=self.config.get("destinationField", "")
                ))

    def setupUI(self):
        self.setWindowTitle("LexiSage设置")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # 创建选项卡
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # 基本设置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        tabs.addTab(basic_tab, "基本设置")

        # 使用水平布局组合笔记类型配置区域和设置区域
        note_type_config_layout = QHBoxLayout()
        basic_layout.addLayout(note_type_config_layout)

        # 笔记类型配置区域（左侧）
        note_configs_group = QGroupBox("笔记类型列表")
        note_configs_layout = QVBoxLayout(note_configs_group)
        note_configs_group.setMaximumWidth(200)  # 限制宽度

        # 添加笔记类型列表
        self.note_configs_list = QListWidget()
        self.note_configs_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.note_configs_list.itemSelectionChanged.connect(self.on_note_config_selected)
        note_configs_layout.addWidget(self.note_configs_list)

        # 按钮区域
        buttons_layout = QHBoxLayout()
        self.add_config_btn = QPushButton("+")
        self.add_config_btn.setToolTip("添加配置")
        self.add_config_btn.setMaximumWidth(30)
        self.add_config_btn.clicked.connect(self.add_note_type_config)

        self.remove_config_btn = QPushButton("-")
        self.remove_config_btn.setToolTip("删除配置")
        self.remove_config_btn.setMaximumWidth(30)
        self.remove_config_btn.clicked.connect(self.remove_note_type_config)
        self.remove_config_btn.setEnabled(False)  # 初始禁用

        buttons_layout.addWidget(self.add_config_btn)
        buttons_layout.addWidget(self.remove_config_btn)
        buttons_layout.addStretch(1)
        note_configs_layout.addLayout(buttons_layout)

        note_type_config_layout.addWidget(note_configs_group)

        # 笔记类型设置区域（右侧）
        self.note_type_settings_group = QGroupBox("笔记类型设置")
        self.note_type_settings_group.setEnabled(False)  # 初始禁用
        note_type_layout = QFormLayout(self.note_type_settings_group)

        # 笔记类型选择
        self.note_type_combo = QComboBox()
        self.populate_note_types()
        note_type_layout.addRow("笔记类型:", self.note_type_combo)

        # 字段选择区域
        self.field_to_explain_combo = QComboBox()
        self.context_field_combo = QComboBox()
        self.context_field_combo.addItem("无")
        self.destination_field_combo = QComboBox()

        note_type_layout.addRow("要解释的字段:", self.field_to_explain_combo)
        note_type_layout.addRow("上下文字段(可选):", self.context_field_combo)
        note_type_layout.addRow("释义目标字段:", self.destination_field_combo)

        # 保存按钮
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_current_note_type_config)
        note_type_layout.addRow("", self.save_config_btn)

        note_type_config_layout.addWidget(self.note_type_settings_group, 1)  # 添加伸展因子，右侧占更多空间

        # 自定义提示词
        prompt_group = QGroupBox("自定义提示词")
        prompt_layout = QVBoxLayout(prompt_group)

        # 系统提示词
        self.system_prompt_edit = QPlainTextEdit()
        self.system_prompt_edit.setPlaceholderText("给AI的指令，设置AI的行为、角色和约束")
        self.system_prompt_edit.setMinimumHeight(100)
        prompt_layout.addWidget(self.system_prompt_edit)

        # 说明文本
        prompt_info = QLabel("提示：在这里设置AI的行为方式和风格，以控制生成结果的语气和格式")
        prompt_info.setStyleSheet("color: gray; font-size: 11px;")
        prompt_info.setWordWrap(True)
        prompt_layout.addWidget(prompt_info)

        basic_layout.addWidget(prompt_group)

        # AI服务选项卡
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        tabs.addTab(ai_tab, "AI服务设置")

        # 使用水平布局放置标签和下拉框在同一行
        service_selection_layout = QHBoxLayout()
        service_label = QLabel("选择AI服务:")
        self.ai_service_combo = QComboBox()
        self.ai_service_combo.addItems(["OpenAI", "XAI", "DeepSeek"])
        self.ai_service_combo.setMaximumWidth(200)  # 限制下拉框宽度
        service_selection_layout.addWidget(service_label)
        service_selection_layout.addWidget(self.ai_service_combo)
        service_selection_layout.addStretch(1)  # 添加弹性空间
        ai_layout.addLayout(service_selection_layout)

        # 创建服务配置区域
        self.service_stack = QStackedWidget()
        self.ai_service_combo.currentIndexChanged.connect(self.service_stack.setCurrentIndex)
        ai_layout.addWidget(self.service_stack)

        # OpenAI 配置
        openai_widget = QWidget()
        openai_layout = QFormLayout(openai_widget)
        self.openai_baseurl = QLineEdit()
        self.openai_baseurl.setMinimumWidth(300)  # 设置最小宽度
        self.openai_baseurl.setText("https://api.openai.com/v1/chat/completions")  # 默认填写
        self.openai_apikey = QLineEdit()
        self.openai_apikey.setMinimumWidth(300)  # 设置最小宽度
        self.openai_model = QLineEdit()
        self.openai_model.setMinimumWidth(300)  # 设置最小宽度
        self.openai_model.setText("gpt-3.5-turbo")  # 默认填写模型

        # 添加OpenAI URL格式提示
        openai_url_hint = QLabel("填写完整URL，例如: https://api.openai.com/v1/chat/completions")
        openai_url_hint.setStyleSheet("color: gray; font-size: 11px;")

        openai_layout.addRow("Base URL:", self.openai_baseurl)
        openai_layout.addRow(openai_url_hint)
        openai_layout.addRow("API Key:", self.openai_apikey)
        openai_layout.addRow("Model:", self.openai_model)
        self.service_stack.addWidget(openai_widget)

        # XAI 配置
        xai_widget = QWidget()
        xai_layout = QFormLayout(xai_widget)
        self.xai_baseurl = QLineEdit()
        self.xai_baseurl.setMinimumWidth(300)  # 设置最小宽度
        self.xai_apikey = QLineEdit()
        self.xai_apikey.setMinimumWidth(300)  # 设置最小宽度
        self.xai_model = QLineEdit()
        self.xai_model.setMinimumWidth(300)  # 设置最小宽度

        # 添加XAI URL格式提示
        xai_url_hint = QLabel("填写完整URL，例如: https://api.x.ai/v1/chat/completions")
        xai_url_hint.setStyleSheet("color: gray; font-size: 11px;")

        xai_layout.addRow("Base URL:", self.xai_baseurl)
        xai_layout.addRow(xai_url_hint)
        xai_layout.addRow("API Key:", self.xai_apikey)
        xai_layout.addRow("Model:", self.xai_model)
        self.service_stack.addWidget(xai_widget)

        # DeepSeek 配置
        deepseek_widget = QWidget()
        deepseek_layout = QFormLayout(deepseek_widget)
        self.deepseek_baseurl = QLineEdit()
        self.deepseek_baseurl.setMinimumWidth(300)  # 设置最小宽度
        self.deepseek_baseurl.setText("https://api.deepseek.com/chat/completions")  # 更新为正确的URL
        self.deepseek_apikey = QLineEdit()
        self.deepseek_apikey.setMinimumWidth(300)  # 设置最小宽度
        self.deepseek_model = QLineEdit()
        self.deepseek_model.setMinimumWidth(300)  # 设置最小宽度
        self.deepseek_model.setText("deepseek-chat")  # 默认填写模型

        # 添加DeepSeek URL格式提示
        deepseek_url_hint = QLabel("填写完整URL，例如: https://api.deepseek.com/chat/completions")
        deepseek_url_hint.setStyleSheet("color: gray; font-size: 11px;")

        deepseek_layout.addRow("Base URL:", self.deepseek_baseurl)
        deepseek_layout.addRow(deepseek_url_hint)
        deepseek_layout.addRow("API Key:", self.deepseek_apikey)
        deepseek_layout.addRow("Model:", self.deepseek_model)
        self.service_stack.addWidget(deepseek_widget)

        # 按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 连接信号
        self.note_type_combo.currentIndexChanged.connect(self.on_note_type_changed)

        # 刷新笔记类型列表
        self.refresh_note_configs_list()

        # 加载AI服务和系统提示词配置
        self.load_config()

    def populate_note_types(self):
        self.note_type_combo.clear()
        for note_type in sorted(mw.col.models.all(), key=lambda x: x["name"].lower()):
            self.note_type_combo.addItem(note_type["name"])

    def on_note_type_changed(self, index):
        self.field_to_explain_combo.clear()
        self.context_field_combo.clear()
        self.destination_field_combo.clear()

        # 添加"无"选项到上下文字段
        self.context_field_combo.addItem("无")

        if index >= 0:
            note_type_name = self.note_type_combo.currentText()
            note_type = mw.col.models.by_name(note_type_name)
            if note_type:
                for field in note_type["flds"]:
                    field_name = field["name"]
                    self.field_to_explain_combo.addItem(field_name)
                    self.context_field_combo.addItem(field_name)
                    self.destination_field_combo.addItem(field_name)

    def refresh_note_configs_list(self):
        self.note_configs_list.clear()
        for config in self.note_type_configs:
            item = QListWidgetItem(config.note_type)
            item.setData(Qt.ItemDataRole.UserRole, config)
            self.note_configs_list.addItem(item)

    def on_note_config_selected(self):
        items = self.note_configs_list.selectedItems()
        if items:
            self.note_type_settings_group.setEnabled(True)
            self.remove_config_btn.setEnabled(True)

            # 获取选中的配置
            config = items[0].data(Qt.ItemDataRole.UserRole)

            # 设置笔记类型
            index = self.note_type_combo.findText(config.note_type)
            if index >= 0:
                self.note_type_combo.setCurrentIndex(index)
                self.on_note_type_changed(index)

                # 设置字段
                if config.field_to_explain:
                    index = self.field_to_explain_combo.findText(config.field_to_explain)
                    if index >= 0:
                        self.field_to_explain_combo.setCurrentIndex(index)

                if config.context_field:
                    index = self.context_field_combo.findText(config.context_field)
                    if index >= 0:
                        self.context_field_combo.setCurrentIndex(index)
                else:
                    self.context_field_combo.setCurrentIndex(0)  # "无"

                if config.destination_field:
                    index = self.destination_field_combo.findText(config.destination_field)
                    if index >= 0:
                        self.destination_field_combo.setCurrentIndex(index)
        else:
            self.note_type_settings_group.setEnabled(False)
            self.remove_config_btn.setEnabled(False)

    def add_note_type_config(self):
        # 创建新配置
        config = NoteTypeConfig()

        # 如果有笔记类型可选，默认选择第一个
        if self.note_type_combo.count() > 0:
            config.note_type = self.note_type_combo.itemText(0)

        # 添加到配置列表
        self.note_type_configs.append(config)

        # 刷新列表并选中新添加的项
        self.refresh_note_configs_list()
        self.note_configs_list.setCurrentRow(self.note_configs_list.count() - 1)

    def remove_note_type_config(self):
        items = self.note_configs_list.selectedItems()
        if items:
            # 获取选中的行
            row = self.note_configs_list.row(items[0])

            # 从配置列表中移除
            del self.note_type_configs[row]

            # 刷新列表
            self.refresh_note_configs_list()

            # 如果还有配置，选中第一个
            if self.note_configs_list.count() > 0:
                self.note_configs_list.setCurrentRow(0)

    def save_current_note_type_config(self):
        items = self.note_configs_list.selectedItems()
        if items:
            # 获取当前选中的配置
            config = items[0].data(Qt.ItemDataRole.UserRole)

            # 更新配置
            config.note_type = self.note_type_combo.currentText()
            config.field_to_explain = self.field_to_explain_combo.currentText()
            config.context_field = self.context_field_combo.currentText() if self.context_field_combo.currentIndex() > 0 else ""
            config.destination_field = self.destination_field_combo.currentText()

            # 刷新显示
            items[0].setText(config.note_type)

            tooltip("笔记类型配置已保存")

    def load_config(self):
        if not self.config:
            return

        # 加载系统提示词
        system_prompt = self.config.get("systemPrompt", "请解释词语或短语「{word}」的意思。{context}")
        self.system_prompt_edit.setPlainText(system_prompt)

        # 加载AI服务设置
        ai_service = self.config.get("aiService", "openai").lower()
        if ai_service == "openai":
            self.ai_service_combo.setCurrentIndex(0)
        elif ai_service == "xai":
            self.ai_service_combo.setCurrentIndex(1)
        elif ai_service == "deepseek":
            self.ai_service_combo.setCurrentIndex(2)

        # 加载API配置
        api_config = self.config.get("apiConfig", {})

        # OpenAI
        openai_config = api_config.get("openai", {})
        self.openai_baseurl.setText(openai_config.get("baseUrl", "https://api.openai.com/v1"))
        self.openai_apikey.setText(openai_config.get("apiKey", ""))
        self.openai_model.setText(openai_config.get("model", "gpt-3.5-turbo"))

        # XAI
        xai_config = api_config.get("xai", {})
        self.xai_baseurl.setText(xai_config.get("baseUrl", ""))
        self.xai_apikey.setText(xai_config.get("apiKey", ""))
        self.xai_model.setText(xai_config.get("model", ""))

        # DeepSeek
        deepseek_config = api_config.get("deepseek", {})
        self.deepseek_baseurl.setText(deepseek_config.get("baseUrl", ""))
        self.deepseek_apikey.setText(deepseek_config.get("apiKey", ""))
        self.deepseek_model.setText(deepseek_config.get("model", ""))

    def save_config(self):
        ai_service_index = self.ai_service_combo.currentIndex()
        ai_service = ["openai", "xai", "deepseek"][ai_service_index]

        # 转换为新的配置格式
        note_type_configs = {}
        for config in self.note_type_configs:
            note_type_configs[config.note_type] = {
                "fieldToExplain": config.field_to_explain,
                "contextField": config.context_field,
                "destinationField": config.destination_field
            }

        # 更新配置
        self.config["noteTypeConfigs"] = note_type_configs
        self.config["aiService"] = ai_service
        self.config["systemPrompt"] = self.system_prompt_edit.toPlainText()

        # API配置
        self.config["apiConfig"] = {
            "openai": {
                "baseUrl": self.openai_baseurl.text(),
                "apiKey": self.openai_apikey.text(),
                "model": self.openai_model.text()
            },
            "xai": {
                "baseUrl": self.xai_baseurl.text(),
                "apiKey": self.xai_apikey.text(),
                "model": self.xai_model.text()
            },
            "deepseek": {
                "baseUrl": self.deepseek_baseurl.text(),
                "apiKey": self.deepseek_apikey.text(),
                "model": self.deepseek_model.text()
            }
        }

        # 保存配置
        mw.addonManager.writeConfig("anki_lexisage", self.config)

    def accept(self):
        # 检查是否至少有一个笔记类型配置
        if not self.note_type_configs:
            showInfo("请至少添加一个笔记类型配置")
            return

        # 检查每个笔记类型配置是否完整
        for config in self.note_type_configs:
            if not config.field_to_explain or not config.destination_field:
                showInfo(f"笔记类型 '{config.note_type}' 的配置不完整，请确保已设置要解释的字段和释义目标字段")
                return

        # 检查API配置
        ai_service_index = self.ai_service_combo.currentIndex()
        ai_service = ["openai", "xai", "deepseek"][ai_service_index]

        if ai_service == "openai":
            if not self.openai_apikey.text():
                showInfo("请输入OpenAI API密钥")
                return
        elif ai_service == "xai":
            if not self.xai_baseurl.text() or not self.xai_apikey.text():
                showInfo("请完整填写XAI配置")
                return
        elif ai_service == "deepseek":
            if not self.deepseek_baseurl.text() or not self.deepseek_apikey.text():
                showInfo("请完整填写DeepSeek配置")
                return

        self.save_config()
        tooltip("配置已保存")
        super().accept()

# 设置配置UI的入口函数
def setup_config_ui(parent):
    dialog = ConfigDialog(parent)
    return dialog.exec()
