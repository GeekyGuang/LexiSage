from aqt import mw
from aqt.utils import showInfo as anki_showInfo, qconnect, tooltip
from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import addHook
from aqt.browser import Browser
from aqt.operations import CollectionOp
import time
import platform

# 辅助函数：安全处理UI事件
def safe_process_events():
    """以安全的方式处理UI事件，确保Windows上不会出现窗口问题"""
    QApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents)

# 自定义信息显示函数，使界面更加一致
def showInfo(text, parent=None, title="LexiSage", textFormat="plain"):
    parent = parent or mw

    # 创建自定义信息对话框
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)

    if textFormat == "rich":
        msgBox.setTextFormat(Qt.TextFormat.RichText)
    else:
        msgBox.setTextFormat(Qt.TextFormat.PlainText)

    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Icon.Information)
    msgBox.addButton(QMessageBox.StandardButton.Ok)

    # 显示对话框
    msgBox.exec()

from .config_ui import setup_config_ui
from .ai_service import generate_explanation, generate_explanations_batch, ExplanationTask

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
            "systemPrompt": "你是一位专业的语言学家和教育者，负责解释词语含义。请提供准确、清晰、易懂的解释，适合语言学习者。",
            "maxConcurrentRequests": 3,
            "enableMultiThreading": True
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

        # 显示进度对话框 - 使用特定设置防止Windows上弹出主界面
    parent_window = editor.parentWindow

    progress = QProgressDialog(parent_window)
    progress.setWindowTitle("LexiSage - 生成释义")
    progress.setLabelText("正在生成释义...")
    progress.setCancelButtonText("取消")
    progress.setRange(0, 100)
    progress.setMinimumWidth(300)
    progress.setMinimumDuration(0)  # 立即显示，不等待
    # 关键：使用WindowModal模式避免激活主窗口
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setAutoClose(True)
    progress.setValue(10)  # 立即显示一些进度

    # 设置窗口标志，确保它总是在顶层但不获取主窗口焦点
    progress.setWindowFlags(Qt.WindowType.Dialog |
                           Qt.WindowType.CustomizeWindowHint |
                           Qt.WindowType.WindowTitleHint |
                           Qt.WindowType.WindowCloseButtonHint)

    # 确保进度对话框显示在编辑器窗口上方
    progress.setParent(parent_window)

    # 使用open()而不是show()
    progress.open()
    safe_process_events()  # 确保UI响应

    # 更新进度
    progress.setValue(20)
    progress.setLabelText(f"正在处理: '{word}'")
    safe_process_events()  # 确保UI响应

    # 检查是否取消
    if progress.wasCanceled():
        progress.close()
        return

    # 生成释义
    try:
        explanation = generate_explanation(word, context, config)
        # 检查是否在API调用后取消
        if progress.wasCanceled():
            progress.close()
            return
    except Exception as e:
        showInfo(f"生成释义时发生错误: {str(e)}", title="LexiSage - 错误")
        progress.close()
        return

    # 更新进度
    progress.setValue(80)
    progress.setLabelText("正在更新笔记...")
    safe_process_events()  # 确保UI响应

    # 最后检查一次是否取消
    if progress.wasCanceled():
        progress.close()
        return

    if explanation:
        # 将纯文本换行转换为HTML换行标签
        explanation = explanation.replace("\n", "<br>")
        # 更新目标字段
        note[destination_field] = explanation
        note.flush()
        editor.loadNote()

        # 完成
        progress.setValue(100)
        progress.setLabelText("完成!")
        safe_process_events()

        # 最后一次检查取消状态
        if progress.wasCanceled():
            progress.close()
            return

        # 显示结果
        result_msg = f"""<h3>释义生成成功</h3>
<p>已更新字段: <b>{destination_field}</b></p>"""
        showInfo(result_msg, title="LexiSage - 生成释义", textFormat="rich")
    else:
        # 完成但有错误
        progress.setValue(100)
        progress.setLabelText("生成失败")
        safe_process_events()

        # 即使失败也检查取消状态
        if progress.wasCanceled():
            progress.close()
            return

        showInfo("释义生成失败，请检查配置和网络连接", title="LexiSage - 错误")

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

    # 延迟一小段时间后强制更新侧边栏 - 使用QTimer确保UI更新完成后再执行
    QTimer.singleShot(100, lambda: fix_sidebar_visibility(browser))

    # 强制QApplication处理事件，确保UI更新
    safe_process_events()

# 修复侧边栏可见性问题
def fix_sidebar_visibility(browser):
    # 检查不同版本Anki的侧边栏结构
    if hasattr(browser, 'sidebarDockWidget') and hasattr(browser.sidebarDockWidget, 'setVisible'):
        # Anki 2.1.50+的结构
        browser.sidebarDockWidget.setVisible(True)
    elif hasattr(browser, 'form') and hasattr(browser.form, 'filterButton'):
        # 一些Anki版本使用filterButton
        browser.form.filterButton.click()
        browser.form.filterButton.click()  # 点击两次以确保显示
    elif hasattr(browser, 'form') and hasattr(browser.form, 'splitter'):
        # 另一种可能的结构
        sizes = browser.form.splitter.sizes()
        if sizes[0] == 0:
            sizes[0] = 200  # 设置侧边栏宽度
            browser.form.splitter.setSizes(sizes)

    # 尝试直接访问侧边栏组件并强制更新
    try:
        if hasattr(browser, 'sidebar'):
            browser.sidebar.refresh()
        elif hasattr(browser, 'sidebarTree'):
            browser.sidebarTree.refresh()
    except:
        pass  # 忽略可能的错误

    # 强制处理事件以确保UI更新
    safe_process_events()

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
    enable_multithreading = config.get("enableMultiThreading", True)
    max_concurrent = config.get("maxConcurrentRequests", 3)

    multithreading_status = "启用" if enable_multithreading else "禁用"
    confirm_msg = f"""确定要为选中的{len(selected_notes)}条笔记生成释义吗？

多线程: {multithreading_status}
{f'并发数: {max_concurrent}' if enable_multithreading else ''}"""

    if not askUser(confirm_msg):
        return

    # 创建一个更好的进度对话框 - 以特定方式避免Windows上弹出主界面
    browser_window = browser
    if hasattr(browser, 'window'):
        browser_window = browser.window()

    progress = QProgressDialog(browser_window)
    progress.setWindowTitle("LexiSage - 生成释义")
    progress.setLabelText("准备中...")
    progress.setCancelButtonText("取消")
    progress.setRange(0, len(selected_notes))
    progress.setMinimumWidth(350)
    progress.setMinimumDuration(0)  # 立即显示，不等待
    progress.setAutoClose(False)
    progress.setValue(0)

    # 关键设置：使用DialogModal模式和正确的父窗口，避免激活主窗口
    progress.setWindowModality(Qt.WindowModality.WindowModal)

    # 设置窗口标志，确保它总是在顶层但不获取主窗口焦点
    progress.setWindowFlags(Qt.WindowType.Dialog |
                           Qt.WindowType.CustomizeWindowHint |
                           Qt.WindowType.WindowTitleHint |
                           Qt.WindowType.WindowCloseButtonHint)

    # 将对话框设置为browser的子窗口，而非主窗口的子窗口
    progress.setParent(browser_window)

    # 开始显示进度条
    progress.open()

    # 增加刷新UI的频率 - 使用更安全的方式处理事件
    safe_process_events()

    # 计数器
    success_count = 0
    error_count = 0
    note_type_mismatch = 0
    empty_field = 0

    # 添加标志跟踪是否真正被用户取消
    was_canceled = False

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
        # 准备任务列表
        tasks = []
        total_notes = len(selected_notes)

        # 预处理所有笔记，创建任务列表
        for nid in selected_notes:
            if progress.wasCanceled():
                was_canceled = True
                break

            note = mw.col.get_note(nid)

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

            # 创建任务对象
            task = ExplanationTask(nid, word, context, config, note_type_config)
            tasks.append(task)

        if was_canceled:
            progress.close()
            showInfo("操作已取消", title="LexiSage - 已取消")
            return

        # 更新进度条范围
        progress.setRange(0, len(tasks))
        progress.setValue(0)
        progress.setLabelText(f"开始处理 {len(tasks)} 个任务...")
        safe_process_events()

        # 进度回调函数
        def progress_callback(completed, total, current_word):
            if progress.wasCanceled():
                return
            progress.setValue(completed)
            if current_word:
                progress.setLabelText(f"正在处理: '{current_word}' ({completed}/{total})")
            safe_process_events()

        # 根据配置选择处理方式
        if enable_multithreading and len(tasks) > 1:
            # 使用多线程处理
            completed_tasks = generate_explanations_batch(
                tasks,
                max_workers=max_concurrent,
                progress_callback=progress_callback
            )
        else:
            # 使用单线程处理（保留原有逻辑）
            completed_tasks = []
            for i, task in enumerate(tasks):
                if progress.wasCanceled():
                    was_canceled = True
                    break

                progress.setValue(i)
                progress.setLabelText(f"正在处理: '{task.word}' ({i+1}/{len(tasks)})")
                safe_process_events()

                try:
                    explanation = generate_explanation(task.word, task.context, config)
                    if explanation:
                        task.result = explanation.replace("\n", "<br>")
                        task.success = True
                    else:
                        task.error = "API调用失败"
                        task.success = False
                except Exception as e:
                    task.error = str(e)
                    task.success = False

                completed_tasks.append(task)

                # 短暂延迟，避免API请求过于频繁
                time.sleep(0.1)
                safe_process_events()

        # 如果用户在处理过程中取消了操作
        if progress.wasCanceled():
            was_canceled = True

        # 更新笔记数据
        if not was_canceled:
            progress.setLabelText("保存结果...")
            safe_process_events()

            for task in completed_tasks:
                if task.success and task.result:
                    note = mw.col.get_note(task.note_id)
                    note[task.note_type_config["destinationField"]] = task.result
                    note.flush()
                    success_count += 1
                else:
                    error_count += 1

    except Exception as e:
        # 捕获整个过程中的异常
        showInfo(f"处理过程中发生错误: {str(e)}", title="LexiSage - 错误")

    finally:
        # 完成所有处理后，确保进度条显示已完成
        if not progress.wasCanceled():
            progress.setValue(len(selected_notes))
            progress.setLabelText("完成!")
        safe_process_events()

        # 关闭进度对话框
        progress.close()

    # 如果用户确实取消了操作，显示部分结果
    if was_canceled:
        showInfo("操作已取消", title="LexiSage - 已取消")
        browser.model.reset()
        return

    # 显示结果，以更简洁、用户友好的方式呈现
    total_processed = success_count + error_count + note_type_mismatch + empty_field
    result_msg = f"""
<h3>处理完成</h3>
<table cellpadding=6>
  <tr>
    <td><b>总处理:</b></td>
    <td align="right">{total_processed}</td>
  </tr>
  <tr>
    <td><b>成功:</b></td>
    <td align="right">{success_count}</td>
  </tr>
  <tr>
    <td><b>失败:</b></td>
    <td align="right">{error_count}</td>
  </tr>
  <tr>
    <td><b>笔记类型未配置:</b></td>
    <td align="right">{note_type_mismatch}</td>
  </tr>
  <tr>
    <td><b>源字段为空:</b></td>
    <td align="right">{empty_field}</td>
  </tr>
</table>
"""
    showInfo(result_msg, title="LexiSage - 生成释义结果", textFormat="rich")

    # 刷新浏览器视图
    browser.model.reset()

# 确认对话框
def askUser(text, parent=None, defaultButton=QMessageBox.StandardButton.Yes, title="LexiSage - 确认"):
    parent = parent or mw

    # 创建自定义确认对话框
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Icon.Question)

    # 添加按钮
    yesButton = msgBox.addButton("确定", QMessageBox.ButtonRole.YesRole)
    noButton = msgBox.addButton("取消", QMessageBox.ButtonRole.NoRole)

    # 设置默认按钮
    msgBox.setDefaultButton(yesButton if defaultButton == QMessageBox.StandardButton.Yes else noButton)

    # 显示对话框
    msgBox.exec()

    # 返回结果
    return msgBox.clickedButton() == yesButton

# 初始化
setup_tools_menu()  # 添加设置到工具菜单
addHook("setupEditorButtons", add_editor_button)
addHook("browser.setupMenus", setup_browser_menu)
