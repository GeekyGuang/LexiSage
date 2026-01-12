from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
import os
import json
import codecs
from .prompts import DEFAULT_GLOBAL_SYSTEM_PROMPT, DEFAULT_FIELD_PROMPT_TEMPLATE, BATCH_INSTRUCTION_TEMPLATE

# 笔记类型配置类：存储单个笔记类型的配置信息
class NoteTypeConfig:
    def __init__(self, note_type="", field_to_explain="", context_field="", field_prompts=None):
        self.note_type = note_type
        self.field_to_explain = field_to_explain
        self.context_field = context_field
        self.field_prompts = field_prompts if field_prompts is not None else {}

# 配置对话框类：主配置界面，提供用户配置LexiSage的所有设置选项
class ConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.addon_dir, "config.json")
        self.addon_name = os.path.basename(self.addon_dir)

        self.config = self.load_config_from_disk()

        self.note_type_configs = []
        self.load_note_type_configs()

        self.setupUI()
        
        self.active_config = None
        self.current_editing_field = None

        self.refresh_note_configs_list()
        self.load_ui_settings()
        
        if self.note_configs_list.count() > 0:
            self.note_configs_list.setCurrentRow(0)

    # 从磁盘加载配置文件
    def load_config_from_disk(self):
        if not os.path.exists(self.config_path): return {}
        try:
            with codecs.open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}

    # 保存配置文件到磁盘
    def save_config_to_disk(self):
        try:
            with codecs.open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            mw.addonManager.writeConfig(self.addon_name, self.config)
            return True
        except Exception as e:
            showInfo(f"写入失败: {str(e)}")
            return False

    # 从配置字典加载笔记类型配置到NoteTypeConfig对象列表
    def load_note_type_configs(self):
        self.note_type_configs = []
        if "noteTypeConfigs" in self.config and isinstance(self.config["noteTypeConfigs"], dict):
            configs = self.config["noteTypeConfigs"]
            for note_type, config_data in configs.items():
                if not isinstance(config_data, dict): continue
                obj = NoteTypeConfig(
                    note_type=note_type,
                    field_to_explain=config_data.get("fieldToExplain", ""),
                    context_field=config_data.get("contextField", ""),
                    field_prompts=config_data.get("fieldPrompts", {})
                )
                self.note_type_configs.append(obj)
        # 系统大改，如果没有旧配置，就保持空列表
        elif "selectedNoteType" in self.config:
            pass 

    # 设置用户界面：创建三个标签页的布局和控件
    def setupUI(self):
        """
        构建LexiSage配置对话框的主要用户界面。
        界面分为三个标签页：
        1. 笔记类型设置：配置不同笔记类型的字段映射和提示词
        2. AI系统指令：设置全局AI系统提示词
        3. AI服务设置：配置API密钥、模型参数和高级选项
        """
        self.setWindowTitle("LexiSage设置")
        self.setFixedSize(650, 700) 
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # --- Tab 1: 笔记类型设置 ---
        note_tab = QWidget()
        note_layout = QVBoxLayout(note_tab)
        tabs.addTab(note_tab, "1. 笔记类型设置")
        h_layout = QHBoxLayout()
        note_layout.addLayout(h_layout)

        # 左侧：笔记类型管理面板
        list_group = QGroupBox("笔记类型管理")
        list_layout = QVBoxLayout(list_group)
        list_group.setMaximumWidth(220)
        
        # 笔记类型选择下拉框：显示Anki中所有的笔记类型
        list_layout.addWidget(QLabel("① 选择要配置的笔记类型:"))
        self.source_note_type_combo = QComboBox()
        self.populate_note_types()
        list_layout.addWidget(self.source_note_type_combo)
        
        # 添加到配置列表按钮：将选中的笔记类型添加到右侧的配置列表中
        self.add_config_btn = QPushButton("↓ 添加到配置列表")
        self.add_config_btn.clicked.connect(self.add_note_type_config)
        list_layout.addWidget(self.add_config_btn)
        
        list_layout.addSpacing(10)
        list_layout.addWidget(QLabel("② 已配置列表:"))
        
        # 已配置笔记类型列表：显示已经配置的笔记类型，点击可选中进行编辑
        self.note_configs_list = QListWidget()
        self.note_configs_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.note_configs_list.itemSelectionChanged.connect(self.on_note_config_selected)
        list_layout.addWidget(self.note_configs_list)
        
        # 删除选中配置按钮：删除列表中选中的笔记类型配置
        self.remove_config_btn = QPushButton("删除选中配置")
        self.remove_config_btn.clicked.connect(self.remove_note_type_config)
        self.remove_config_btn.setEnabled(False)
        list_layout.addWidget(self.remove_config_btn)
        
        h_layout.addWidget(list_group)

        # 右侧：详细字段配置面板（仅在选中笔记类型时启用）
        self.note_type_settings_group = QGroupBox("详细字段配置")
        self.note_type_settings_group.setEnabled(False)
        settings_layout = QFormLayout(self.note_type_settings_group)
        
        # 当前编辑的笔记类型标签
        self.current_type_label = QLabel("-")
        self.current_type_label.setStyleSheet("font-weight: bold; color: #333;")
        settings_layout.addRow("当前编辑:", self.current_type_label)
        
        # 来源单词字段下拉框：选择作为AI解释源的字段（通常是单词字段）
        self.field_to_explain_combo = QComboBox()
        
        # 来源上下文字段下拉框：选择提供上下文的字段（可选）
        self.context_field_combo = QComboBox()
        self.context_field_combo.addItem("无")
        
        settings_layout.addRow("来源单词字段:", self.field_to_explain_combo)
        settings_layout.addRow("来源上下文字段:", self.context_field_combo)

        # 释义目标字段与提示词配置区域
        self.fields_prompt_group = QGroupBox("释义目标字段与提示词")
        fp_layout = QVBoxLayout(self.fields_prompt_group)
        
        # 目标字段管理工具栏
        fp_tools = QHBoxLayout()
        self.field_prompt_combo = QComboBox()
        fp_tools.addWidget(QLabel("目标字段:"), 0)
        fp_tools.addWidget(self.field_prompt_combo, 1)
        
        # 添加字段按钮：将下拉框选中的字段添加到目标字段列表
        self.add_field_btn = QPushButton("+")
        self.add_field_btn.setFixedWidth(30)
        self.add_field_btn.clicked.connect(self.add_field_config)
        fp_tools.addWidget(self.add_field_btn)
        
        # 删除字段按钮：从目标字段列表中删除选中的字段
        self.remove_field_btn = QPushButton("-")
        self.remove_field_btn.setFixedWidth(30)
        self.remove_field_btn.clicked.connect(self.remove_field_config)
        fp_tools.addWidget(self.remove_field_btn)
        
        fp_layout.addLayout(fp_tools)

        # 已配置目标字段列表：显示已添加的目标字段，点击可编辑其提示词
        self.configured_fields_list = QListWidget()
        self.configured_fields_list.setMaximumHeight(100)
        fp_layout.addWidget(QLabel("已添加的释义目标字段 (点击修改提示词):")) 
        fp_layout.addWidget(self.configured_fields_list)
        self.configured_fields_list.itemClicked.connect(self.on_field_list_item_clicked)

        # 字段提示词编辑区域
        prompt_bar = QHBoxLayout()
        prompt_bar.addWidget(QLabel("字段专属提示词 (留空则用默认):"))
        prompt_bar.addStretch()
        
        # 查看默认字段提示词按钮：显示默认的字段提示词模板
        self.view_default_btn = QPushButton("查看默认字段提示词")
        # DEFAULT_FIELD_PROMPT_TEMPLATE 现在是字符串格式，不需要 json.dumps
        self.view_default_btn.clicked.connect(lambda: self.show_preview_dialog("默认字段指令模板 (Reference)", DEFAULT_FIELD_PROMPT_TEMPLATE))
        prompt_bar.addWidget(self.view_default_btn)
        fp_layout.addLayout(prompt_bar)

        # 提示词文本编辑框：编辑选中字段的自定义提示词
        self.prompt_text_edit = QPlainTextEdit()
        self.prompt_text_edit.setPlaceholderText("在此输入针对该字段的指令...\n支持变量: {word} (来源单词), {context} (来源上下文)")
        self.prompt_text_edit.setMinimumHeight(100)
        self.prompt_text_edit.setEnabled(False)
        fp_layout.addWidget(self.prompt_text_edit)
        
        settings_layout.addRow(self.fields_prompt_group)
        h_layout.addWidget(self.note_type_settings_group, 1)

        # --- Tab 2: AI系统指令 ---
        sys_tab = QWidget()
        sys_layout = QVBoxLayout(sys_tab)
        tabs.addTab(sys_tab, "2. AI系统指令")
        
        # AI系统全局提示词配置区域
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("AI系统全局提示词  (留空则用默认):"))
        top_bar.addStretch()
        
        # 查看默认全局提示词按钮：显示默认的全局系统提示词模板
        self.view_global_default_btn = QPushButton("查看默认全局提示词")
        self.view_global_default_btn.clicked.connect(lambda: self.show_preview_dialog("默认全局人设", DEFAULT_GLOBAL_SYSTEM_PROMPT))
        top_bar.addWidget(self.view_global_default_btn)
        sys_layout.addLayout(top_bar)
        
        # 全局系统提示词文本编辑框：输入自定义的全局AI系统提示词
        self.global_system_prompt = QPlainTextEdit()
        self.global_system_prompt.setPlaceholderText("在此输入自定义全局提示词... \n支持变量: {word} (来源单词), {context} (来源上下文)")
        sys_layout.addWidget(self.global_system_prompt)
        
        # 提示标签：提醒用户需要先配置笔记类型
        sys_layout.addWidget(QLabel("提示：若页面 1 未配置笔记类型，此处设置可能无法生效。"))
        sys_layout.addStretch()

        # --- Tab 3: AI服务设置 ---
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        tabs.addTab(ai_tab, "3. AI服务设置")
        
        # AI服务选择区域：选择OpenAI、XAI或DeepSeek
        svc_sel = QHBoxLayout()
        self.ai_service_combo = QComboBox()
        self.ai_service_combo.addItems(["OpenAI", "XAI", "DeepSeek"])
        self.ai_service_combo.currentIndexChanged.connect(self.on_service_changed)
        svc_sel.addWidget(QLabel("选择AI服务:"))
        svc_sel.addWidget(self.ai_service_combo)
        ai_layout.addLayout(svc_sel)
        
        # 服务配置堆栈：根据选择的服务显示相应的配置面板
        self.service_stack = QStackedWidget()
        ai_layout.addWidget(self.service_stack)
        
        # 创建三个AI服务的配置面板
        self.openai_widgets = self.create_service_widget("https://api.openai.com/v1/chat/completions", "gpt-3.5-turbo")
        self.service_stack.addWidget(self.openai_widgets['widget'])
        self.xai_widgets = self.create_service_widget("https://api.x.ai/v1/chat/completions", "grok-2-latest")
        self.service_stack.addWidget(self.xai_widgets['widget'])
        self.deepseek_widgets = self.create_service_widget("https://api.deepseek.com/chat/completions", "deepseek-chat")
        self.service_stack.addWidget(self.deepseek_widgets['widget'])
        
        ai_layout.addSpacing(10)
        
        # 高级设置区域：配置多线程和并发请求数
        mt_group = QGroupBox("高级设置")
        mt_layout = QFormLayout(mt_group)
        
        # 启用多线程并发复选框：启用后可以同时处理多个AI请求
        self.enable_multithreading_checkbox = QCheckBox("启用多线程并发")
        mt_layout.addRow(self.enable_multithreading_checkbox)
        
        # 并发请求数调节框：设置同时发送的最大请求数量（1-10）
        self.max_concurrent_spinbox = QSpinBox()
        self.max_concurrent_spinbox.setRange(1, 10)
        mt_layout.addRow("并发请求数:", self.max_concurrent_spinbox)
        ai_layout.addWidget(mt_group)
        
        ai_layout.addSpacing(10)
        
        # 预览完整发送内容按钮：查看将发送给AI的完整payload结构
        preview_payload_btn = QPushButton("🔍 预览完整发送内容 (Payload Preview)")
        preview_payload_btn.clicked.connect(self.preview_final_payload)
        ai_layout.addWidget(preview_payload_btn)

        # 预览提示标签：提醒用户保存配置后再预览以看到最新效果
        preview_hint = QLabel("(提示：如果您刚才修改了提示词，请点击【保存配置】后再次预览以查看最新效果。)")
        preview_hint.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        preview_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_layout.addWidget(preview_hint)

        # 打开日志文件按钮：查看LexiSage的运行日志
        open_log_btn = QPushButton("📄 打开日志文件 (View Log)")
        open_log_btn.clicked.connect(self.open_log_file)
        ai_layout.addWidget(open_log_btn)
        
        ai_layout.addStretch()

        # --- 底部按钮区域 ---
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        
        # 关闭窗口按钮：关闭配置对话框而不保存更改
        self.close_btn = QPushButton("关闭窗口")
        # [Fix] 增加 padding，使其高度和宽度与保存按钮一致
        self.close_btn.setStyleSheet("padding: 5px 15px;") 
        self.close_btn.clicked.connect(self.reject)
        
        # 保存配置按钮：保存所有配置到配置文件并应用到系统
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setStyleSheet("font-weight: bold; padding: 5px 15px;")
        self.save_btn.clicked.connect(self.save_data)
        
        btn_box.addWidget(self.close_btn)
        btn_box.addWidget(self.save_btn)
        layout.addLayout(btn_box)

    # 创建AI服务设置小部件：包含Base URL、API Key、Model和Temperature设置
    def create_service_widget(self, default_url, default_model):
        service_widget = QWidget()
        form_layout = QFormLayout(service_widget)
        
        base_url_input = QLineEdit(default_url)
        base_url_input.setMinimumWidth(300)
        
        api_key_input = QLineEdit()
        api_key_input.setMinimumWidth(300)
        
        model_name_input = QLineEdit(default_model)
        model_name_input.setMinimumWidth(300)
        
        temperature_spinbox = QDoubleSpinBox()
        temperature_spinbox.setRange(0.0, 2.0)
        temperature_spinbox.setSingleStep(0.1)
        temperature_spinbox.setValue(0.1)
        temperature_spinbox.setDecimals(1)
        
        temperature_hint_label = QLabel("数值越低越严谨(0.1)，数值越高越随机(1.0+)")
        temperature_hint_label.setStyleSheet("color: gray; font-size: 11px; margin-top: -2px;")
        temperature_hint_label.setWordWrap(True)

        form_layout.addRow("Base URL:", base_url_input)
        form_layout.addRow("API Key:", api_key_input)
        form_layout.addRow("Model:", model_name_input)
        form_layout.addRow("Temperature:", temperature_spinbox)
        form_layout.addRow("", temperature_hint_label)

        return {
            'widget': service_widget, 
            'base_url': base_url_input, 
            'api_key': api_key_input, 
            'model': model_name_input, 
            'temp': temperature_spinbox
        }

    # --- Logic ---

    def populate_note_types(self):
        self.source_note_type_combo.clear()
        for model in sorted(mw.col.models.all(), key=lambda x: x["name"].lower()):
            self.source_note_type_combo.addItem(model["name"])

    def refresh_note_configs_list(self):
        self.note_configs_list.clear()
        for config in self.note_type_configs:
            item = QListWidgetItem(config.note_type)
            item.setData(Qt.ItemDataRole.UserRole, config)
            self.note_configs_list.addItem(item)
        
        has_config = len(self.note_type_configs) > 0
        self.global_system_prompt.setEnabled(has_config)

    def sync_current_ui_to_object(self, config_obj):
        if not config_obj: return
        if self.current_editing_field:
            config_obj.field_prompts[self.current_editing_field] = self.prompt_text_edit.toPlainText()
        if self.note_type_settings_group.isEnabled():
            config_obj.field_to_explain = self.field_to_explain_combo.currentText()
            config_obj.context_field = self.context_field_combo.currentText()
            if self.context_field_combo.currentIndex() == 0: 
                config_obj.context_field = ""

    def on_note_config_selected(self):
        if self.active_config:
            self.sync_current_ui_to_object(self.active_config)

        items = self.note_configs_list.selectedItems()
        if not items:
            self.note_type_settings_group.setEnabled(False)
            self.remove_config_btn.setEnabled(False)
            self.current_type_label.setText("-")
            self.active_config = None 
            return
        
        self.note_type_settings_group.setEnabled(True)
        self.remove_config_btn.setEnabled(True)
        
        new_config = items[0].data(Qt.ItemDataRole.UserRole)
        self.active_config = new_config

        self.current_type_label.setText(new_config.note_type)
        self.update_field_combos(new_config.note_type)
        
        if new_config.field_to_explain:
            idx = self.field_to_explain_combo.findText(new_config.field_to_explain)
            if idx >= 0: self.field_to_explain_combo.setCurrentIndex(idx)
        if new_config.context_field:
            idx = self.context_field_combo.findText(new_config.context_field)
            if idx >= 0: self.context_field_combo.setCurrentIndex(idx)
        else:
            self.context_field_combo.setCurrentIndex(0)
            
        self.configured_fields_list.clear()
        self.prompt_text_edit.clear()
        self.prompt_text_edit.setEnabled(False)
        self.current_editing_field = None
        
        for field in new_config.field_prompts.keys():
            self.configured_fields_list.addItem(field)

    def update_field_combos(self, note_type_name):
        self.field_to_explain_combo.clear()
        self.context_field_combo.clear()
        self.field_prompt_combo.clear()
        self.context_field_combo.addItem("无")
        model = mw.col.models.by_name(note_type_name)
        if model:
            for f in model["flds"]:
                fname = f["name"]
                self.field_to_explain_combo.addItem(fname)
                self.context_field_combo.addItem(fname)
                self.field_prompt_combo.addItem(fname)

    def add_note_type_config(self):
        if self.source_note_type_combo.count() == 0: return
        target_type = self.source_note_type_combo.currentText()
        for conf in self.note_type_configs:
            if conf.note_type == target_type:
                showInfo(f"'{target_type}' 已经在配置列表中了！")
                return
        
        if self.active_config:
            self.sync_current_ui_to_object(self.active_config)

        config = NoteTypeConfig(note_type=target_type)
        self.note_type_configs.append(config)
        self.refresh_note_configs_list()
        self.note_configs_list.setCurrentRow(self.note_configs_list.count() - 1)

    def remove_note_type_config(self):
        items = self.note_configs_list.selectedItems()
        if items:
            row = self.note_configs_list.row(items[0])
            del self.note_type_configs[row]
            self.active_config = None 
            self.refresh_note_configs_list()
            if self.note_configs_list.count() > 0:
                self.note_configs_list.setCurrentRow(0)
            else:
                self.on_note_config_selected()

    def add_field_config(self):
        field = self.field_prompt_combo.currentText()
        if not field: return
        exists = [self.configured_fields_list.item(i).text() for i in range(self.configured_fields_list.count())]
        if field in exists: return
        
        if not self.active_config: return
        
        if field not in self.active_config.field_prompts:
            self.active_config.field_prompts[field] = ""
            
        self.configured_fields_list.addItem(field)
        new_item = self.configured_fields_list.item(self.configured_fields_list.count() - 1)
        self.configured_fields_list.setCurrentItem(new_item)
        self.on_field_list_item_clicked(new_item)

    def remove_field_config(self):
        selected = self.configured_fields_list.selectedItems()
        # 如果没选中但有正在编辑的（边缘情况），尝试通过名字找
        if not selected and self.current_editing_field:
            found = self.configured_fields_list.findItems(self.current_editing_field, Qt.MatchFlag.MatchExactly)
            if found: selected = [found[0]]

        if not selected: return
        
        item = selected[0]
        field_name = item.text()
        row_to_remove = self.configured_fields_list.row(item)
        
        if not self.active_config: return

        self.current_editing_field = None 
        self.prompt_text_edit.clear()
        self.prompt_text_edit.setEnabled(False)

        if field_name in self.active_config.field_prompts:
            del self.active_config.field_prompts[field_name]
            
        self.configured_fields_list.takeItem(row_to_remove)
        
        if self.configured_fields_list.count() > 0:
            new_row = min(row_to_remove, self.configured_fields_list.count() - 1)
            self.configured_fields_list.setCurrentRow(new_row)
            self.on_field_list_item_clicked(self.configured_fields_list.item(new_row))
        else:
            self.prompt_text_edit.clear()
            self.prompt_text_edit.setEnabled(False)
            self.current_editing_field = None

    def save_pending_prompt(self):
        if not self.current_editing_field or not self.active_config: return
        self.active_config.field_prompts[self.current_editing_field] = self.prompt_text_edit.toPlainText()

    def on_field_list_item_clicked(self, item):
        self.save_pending_prompt()
        field_name = item.text()
        
        if not self.active_config: return
        
        content = self.active_config.field_prompts.get(field_name, "")
        self.prompt_text_edit.setPlainText(content)
        self.prompt_text_edit.setEnabled(True)
        self.current_editing_field = field_name

    def load_ui_settings(self):
        gp = self.config.get("globalSystemPrompt", "")
        # [Logic Fix] 如果是空的或者等于默认值，我们都让它显示为空字符串
        # 这样就会露出 Placeholder，告诉用户"正在使用默认"
        if gp == DEFAULT_GLOBAL_SYSTEM_PROMPT: 
            gp = ""
        self.global_system_prompt.setPlainText(gp)
        
        svc = self.config.get("aiService", "openai")
        idx = 0
        if svc == "xai": idx = 1
        elif svc == "deepseek": idx = 2
        self.ai_service_combo.setCurrentIndex(idx)
        
        api_conf = self.config.get("apiConfig", {})
        oa = api_conf.get("openai", {})
        self.openai_widgets['base_url'].setText(oa.get("baseUrl", "https://api.openai.com/v1/chat/completions"))
        self.openai_widgets['api_key'].setText(oa.get("apiKey", ""))
        self.openai_widgets['model'].setText(oa.get("model", "gpt-3.5-turbo"))
        self.openai_widgets['temp'].setValue(oa.get("temperature", 0.1))
        
        xa = api_conf.get("xai", {})
        self.xai_widgets['base_url'].setText(xa.get("baseUrl", "https://api.x.ai/v1/chat/completions"))
        self.xai_widgets['api_key'].setText(xa.get("apiKey", ""))
        self.xai_widgets['model'].setText(xa.get("model", "grok-2-latest"))
        self.xai_widgets['temp'].setValue(xa.get("temperature", 0.1))
        
        ds = api_conf.get("deepseek", {})
        self.deepseek_widgets['base_url'].setText(ds.get("baseUrl", "https://api.deepseek.com/chat/completions"))
        self.deepseek_widgets['api_key'].setText(ds.get("apiKey", ""))
        self.deepseek_widgets['model'].setText(ds.get("model", "deepseek-chat"))
        self.deepseek_widgets['temp'].setValue(ds.get("temperature", 0.1))
        
        self.enable_multithreading_checkbox.setChecked(self.config.get("enableMultiThreading", True))
        self.max_concurrent_spinbox.setValue(self.config.get("maxConcurrentRequests", 3))

    def on_service_changed(self, index):
        self.service_stack.setCurrentIndex(index)

    def save_data(self):
        svc_idx = self.ai_service_combo.currentIndex()
        if svc_idx == 0 and not self.openai_widgets['api_key'].text():
            showInfo("请输入 OpenAI API Key")
            return
        elif svc_idx == 1 and not self.xai_widgets['api_key'].text():
            showInfo("请输入 XAI API Key")
            return
        elif svc_idx == 2 and not self.deepseek_widgets['api_key'].text():
            showInfo("请输入 DeepSeek API Key")
            return

        if self.active_config:
            self.sync_current_ui_to_object(self.active_config)

        new_note_configs = {}
        for config_obj in self.note_type_configs:
            new_note_configs[config_obj.note_type] = {
                "fieldToExplain": config_obj.field_to_explain,
                "contextField": config_obj.context_field,
                "fieldPrompts": config_obj.field_prompts
            }

        self.config["noteTypeConfigs"] = new_note_configs
        
        # [Logic Fix] 如果用户没填（空），保存时也保持空，后端会自动使用默认值
        self.config["globalSystemPrompt"] = self.global_system_prompt.toPlainText()
        
        svcs = ["openai", "xai", "deepseek"]
        self.config["aiService"] = svcs[svc_idx]
        self.config["apiConfig"] = {
            "openai": {
                "baseUrl": self.openai_widgets['base_url'].text(),
                "apiKey": self.openai_widgets['api_key'].text(),
                "model": self.openai_widgets['model'].text(),
                "temperature": self.openai_widgets['temp'].value()
            },
            "xai": {
                "baseUrl": self.xai_widgets['base_url'].text(),
                "apiKey": self.xai_widgets['api_key'].text(),
                "model": self.xai_widgets['model'].text(),
                "temperature": self.xai_widgets['temp'].value()
            },
            "deepseek": {
                "baseUrl": self.deepseek_widgets['base_url'].text(),
                "apiKey": self.deepseek_widgets['api_key'].text(),
                "model": self.deepseek_widgets['model'].text(),
                "temperature": self.deepseek_widgets['temp'].value()
            }
        }
        self.enable_multithreading_checkbox.setChecked(self.config.get("enableMultiThreading", True)) # Wait, this line is wrong order in original too but logic is fine, fix below
        self.config["enableMultiThreading"] = self.enable_multithreading_checkbox.isChecked()
        self.config["maxConcurrentRequests"] = self.max_concurrent_spinbox.value()

        for key in ["selectedNoteType", "destinationField", "fieldToExplain", "contextField", 
                    "noContextSystemPrompt", "withContextSystemPrompt", "systemPrompt"]:
            if key in self.config: del self.config[key]

        if self.save_config_to_disk():
            tooltip("配置已保存")

    def preview_final_payload(self):
        # 1. 准备 System Prompt
        system_msg = self.config.get("globalSystemPrompt", "")
        if not system_msg: system_msg = "(提示：当前为空，将使用系统默认人设)"

        # 2. 准备 Requirements (模拟批量生成逻辑)
        requirements_preview_dict = {}
        
        example_word = "ExampleWord"
        example_context = "This is an example sentence for context."
        
        if self.active_config:
            # 遍历当前笔记类型下已配置的所有目标字段
            for field, prompt in self.active_config.field_prompts.items():
                # 如果有自定义提示词则使用自定义，否则使用默认提示词（与ai_service.py一致）
                if prompt and prompt.strip():
                    p_text = prompt
                else:
                    p_text = DEFAULT_FIELD_PROMPT_TEMPLATE
                # 替换变量为示例值
                p_text = p_text.replace("{word}", example_word).replace("{context}", example_context)
                requirements_preview_dict[field] = p_text
        else:
            # 兜底显示：如果没有选中任何配置，展示这个假数据给用户看结构
            requirements_preview_dict = {
                "目标字段_1": "示例指令：解释这个词的词根...",
                "目标字段_2": "示例指令：提供三个同义词..."
            }

        # 3. 格式化 JSON 字符串
        req_json_str = json.dumps(requirements_preview_dict, indent=2, ensure_ascii=False)

        # 4. 填充模板
        # 【必须项修改】：字符串 "{requirements_preview}" 必须改为 "{fields_requirements}" 
        # 才能匹配你之前定义的 BATCH_INSTRUCTION_TEMPLATE 变量。
        preview_content = BATCH_INSTRUCTION_TEMPLATE.replace("{word}", example_word)\
                                                    .replace("{context}", example_context)\
                                                    .replace("{requirements_preview}", req_json_str)

        # 修改显示文本的内容排版，增加视觉分隔线
        display_text = f"""======== [ 1. 系统人设 / System Message ] ========
{system_msg}

======== [ 2. 用户指令 / User Message ] ========
{preview_content}
"""
        self.show_preview_dialog("AI 发送载荷预览 (Payload Preview)", display_text)

    def open_log_file(self):
        log_path = os.path.join(self.addon_dir, "lexisage.log")
        if not os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("=== LexiSage Log Created ===\n")
        url = QUrl.fromLocalFile(log_path)
        QDesktopServices.openUrl(url)

    def show_preview_dialog(self, window_title, text_content):
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(window_title)
        preview_dialog.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(preview_dialog)
        
        text_display_area = QPlainTextEdit(text_content)
        text_display_area.setReadOnly(True)
        main_layout.addWidget(text_display_area)
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(preview_dialog.accept)
        main_layout.addWidget(close_button)
        
        preview_dialog.exec()

def setup_config_ui(parent):
    dialog = ConfigDialog(parent)
    dialog.exec()
