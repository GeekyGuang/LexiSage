from aqt import mw
from aqt.utils import showInfo, qconnect, tooltip
from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import addHook
from aqt.browser import Browser
from aqt.operations import CollectionOp
import time

from .config_ui import setup_config_ui
from .ai_service import generate_explanation

# 初始化配置
def load_config():
    config = mw.addonManager.getConfig(__name__)
    if not config:
        # 设置默认配置
        config = {
            "selectedNoteType": "",
            "fieldToExplain": "",
            "contextField": "",
            "destinationField": "",
            "aiService": "openai",
            "apiConfig": {
                "openai": {
                    "baseUrl": "https://api.openai.com/v1",
                    "apiKey": "",
                    "model": "gpt-3.5-turbo"
                },
                "xai": {
                    "baseUrl": "",
                    "apiKey": "",
                    "model": ""
                },
                "deepseek": {
                    "baseUrl": "",
                    "apiKey": "",
                    "model": ""
                }
            },
            "systemPrompt": "你是一位专业的语言学家和教育者，负责解释词语含义。请提供准确、清晰、易懂的解释，适合语言学习者。"
        }
        mw.addonManager.writeConfig(__name__, config)
    return config

# 打开设置窗口
def open_settings():
    setup_config_ui(mw)

# 添加编辑器按钮 - 适配Anki 24.11版本
def add_editor_button(buttons, editor):
    """
    在Anki 24.11版本中，setupEditorButtons钩子传递的第一个参数是按钮列表，
    第二个参数是编辑器对象
    """
    config = load_config()
    if not config.get("selectedNoteType") or not config.get("fieldToExplain") or not config.get("destinationField"):
        return buttons

    def on_click(editor=editor):
        on_generate_explanation(editor)

    buttons.append(
        editor.addButton(
            icon=None,  # 可以添加图标
            cmd="lexiSage",
            func=on_click,
            tip="生成智能释义",
            label="LexiSage"
        )
    )
    return buttons

# 生成释义的回调函数
def on_generate_explanation(editor):
    config = load_config()
    note = editor.note
    note_type_name = note.note_type()["name"]

    # 从配置中查找对应笔记类型的设置
    note_type_configs = config.get("noteTypeConfigs", {})

    # 检查是否有对应笔记类型的配置
    if note_type_name not in note_type_configs:
        # 尝试使用旧版配置格式
        if "selectedNoteType" in config and config["selectedNoteType"] == note_type_name:
            field_to_explain = config.get("fieldToExplain", "")
            context_field = config.get("contextField", "")
            destination_field = config.get("destinationField", "")
        else:
            showInfo(f"当前笔记类型 '{note_type_name}' 没有配置，请在设置中添加")
            return
    else:
        # 使用新版配置格式
        note_type_config = note_type_configs[note_type_name]
        field_to_explain = note_type_config.get("fieldToExplain", "")
        context_field = note_type_config.get("contextField", "")
        destination_field = note_type_config.get("destinationField", "")

    # 检查字段配置
    if not field_to_explain or not destination_field:
        showInfo(f"笔记类型 '{note_type_name}' 的配置不完整")
        return

    # 获取需要解释的内容
    if field_to_explain not in note:
        showInfo(f"字段 '{field_to_explain}' 不存在于当前笔记")
        return

    word = note[field_to_explain]
    if not word:
        showInfo("要解释的字段为空")
        return

    # 获取上下文内容（如果有）
    context = ""
    if context_field and context_field in note:
        context = note[context_field]

    # 生成释义
    explanation = generate_explanation(word, context, config)
    if explanation:
        # 将纯文本换行转换为HTML换行标签
        explanation = explanation.replace("\n", "<br>")
        # 更新目标字段
        note[destination_field] = explanation
        note.flush()
        editor.loadNote()
        showInfo("释义生成成功")
    else:
        showInfo("释义生成失败，请检查配置和网络连接")

# 为浏览器添加顶级菜单
def setup_browser_menu(browser):
    config = load_config()

    # 创建浏览器中的LexiSage菜单
    lexisage_menu = QMenu("LexiSage", browser)
    browser._lexisage_menu = lexisage_menu  # 直接保存到浏览器对象

    # 获取浏览器菜单栏并添加菜单
    menubar = browser.form.menubar
    # 在帮助菜单之前插入
    help_action = None
    for action in menubar.actions():
        if action.text() == "帮助" or action.text() == "Help":
            help_action = action
            break

    if help_action:
        menubar.insertMenu(help_action, lexisage_menu)
    else:
        menubar.addMenu(lexisage_menu)

    # 添加批量生成菜单项
    bulk_action = QAction("批量生成释义", browser)
    bulk_action.triggered.connect(lambda: on_browser_generate_explanation(browser))
    lexisage_menu.addAction(bulk_action)
    browser._bulk_action = bulk_action  # 保存引用到浏览器对象

    # 添加分隔符
    lexisage_menu.addSeparator()

    # 添加设置菜单项 - 使用简单直接的方式
    def open_settings_from_browser():
        setup_config_ui(mw)

    settings_action = QAction("设置...", browser)
    settings_action.triggered.connect(open_settings_from_browser)
    lexisage_menu.addAction(settings_action)
    browser._settings_action = settings_action  # 保存引用到浏览器对象

    # 强制QApplication处理事件，确保UI更新
    mw.app.processEvents()

# 为工具菜单添加设置选项
def setup_tools_menu():
    # 创建工具菜单下的设置选项
    global tools_settings_action  # 使用全局变量避免垃圾回收
    tools_settings_action = QAction("LexiSage设置...", mw)
    qconnect(tools_settings_action.triggered, open_settings)
    mw.form.menuTools.addAction(tools_settings_action)

# 批量生成释义
def on_browser_generate_explanation(browser):
    config = load_config()

    # 获取选中的笔记ID
    selected_notes = browser.selectedNotes()
    if not selected_notes:
        showInfo("请选择笔记")
        return

    # 确认操作
    if not askUser(f"确定要为选中的{len(selected_notes)}条笔记生成释义吗？"):
        return

    # 处理进度对话框
    progress = QProgressDialog("正在生成释义...", "取消", 0, len(selected_notes), browser)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.show()

    # 计数器
    success_count = 0
    error_count = 0
    note_type_mismatch = 0
    empty_field = 0

    # 获取笔记类型配置
    note_type_configs = config.get("noteTypeConfigs", {})
    # 兼容旧版配置格式
    if not note_type_configs and "selectedNoteType" in config:
        note_type_configs = {
            config["selectedNoteType"]: {
                "fieldToExplain": config.get("fieldToExplain", ""),
                "contextField": config.get("contextField", ""),
                "destinationField": config.get("destinationField", "")
            }
        }

    try:
        for i, nid in enumerate(selected_notes):
            if progress.wasCanceled():
                break

            note = mw.col.get_note(nid)
            progress.setValue(i)
            progress.setLabelText(f"正在处理 {i+1}/{len(selected_notes)}")

            # 获取笔记类型
            note_type_name = note.note_type()["name"]

            # 检查笔记类型是否已配置
            if note_type_name not in note_type_configs:
                note_type_mismatch += 1
                continue

            # 获取当前笔记类型的配置
            note_type_config = note_type_configs[note_type_name]
            field_to_explain = note_type_config.get("fieldToExplain", "")
            context_field = note_type_config.get("contextField", "")
            destination_field = note_type_config.get("destinationField", "")

            # 检查字段配置
            if not field_to_explain or not destination_field:
                showInfo(f"笔记类型 '{note_type_name}' 的配置不完整")
                error_count += 1
                continue

            # 检查源字段是否存在并有内容
            if field_to_explain not in note or not note[field_to_explain]:
                empty_field += 1
                continue

            # 获取内容和上下文
            word = note[field_to_explain]
            context = ""
            if context_field and context_field in note:
                context = note[context_field]

            # 生成释义
            explanation = generate_explanation(word, context, config)
            if explanation:
                # 将纯文本换行转换为HTML换行标签
                explanation = explanation.replace("\n", "<br>")
                # 更新目标字段
                note[destination_field] = explanation
                note.flush()
                success_count += 1
                # 避免API请求过于频繁
                time.sleep(0.5)
            else:
                error_count += 1

            # 更新UI，避免冻结
            mw.app.processEvents()

    finally:
        progress.setValue(len(selected_notes))

    # 显示结果
    result_msg = f"""
处理结果:
- 成功: {success_count}
- 失败: {error_count}
- 笔记类型未配置: {note_type_mismatch}
- 源字段为空: {empty_field}
"""
    showInfo(result_msg)

    # 刷新浏览器视图
    browser.model.reset()

# 确认对话框
def askUser(text, parent=None, defaultButton=QMessageBox.StandardButton.Yes):
    parent = parent or mw
    return QMessageBox.question(parent, "LexiSage", text,
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                defaultButton) == QMessageBox.StandardButton.Yes

# 初始化
setup_tools_menu()  # 添加设置到工具菜单
addHook("setupEditorButtons", add_editor_button)
addHook("browser.setupMenus", setup_browser_menu)
