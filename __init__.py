from aqt import mw
from aqt.utils import tooltip, showInfo
from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import addHook
from aqt.browser import Browser
import re

# 导入依赖模块
from .config_ui import setup_config_ui
from .ai_service import generate_explanations_batch, ExplanationTask, generate_batch_explanation

# --- 辅助函数：用于配置加载和字段检查 ---

def load_config():
    return mw.addonManager.getConfig(__name__)

def open_settings():
    setup_config_ui(mw)

def is_field_visually_empty(text):
    """检测字段是否视觉上为空（忽略HTML标签和空格）"""
    if not text: return True
    text = text.replace("&nbsp;", " ")
    text = re.sub(r'<[^>]+>', '', text)
    return not bool(text.strip())

# --- Worker Thread (后台线程)：用于后台批量生成释义，避免界面卡顿 ---

class BatchGenerationWorker(QThread):
    progress_signal = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, tasks, config):
        super().__init__()
        self.tasks = tasks
        self.config = config
        self.is_cancelled = False

    def run(self):
        try:
            def service_callback(completed, total, word):
                if self.is_cancelled: return
                self.progress_signal.emit(completed, total, word)

            max_workers = self.config.get("maxConcurrentRequests", 3) if self.config.get("enableMultiThreading", True) else 1
            results = generate_explanations_batch(self.tasks, max_workers, service_callback)
            
            if not self.is_cancelled:
                self.finished_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(str(e))

    def cancel(self): 
        self.is_cancelled = True

# --- 浏览器批量逻辑：在浏览器中为选中的笔记批量生成释义 ---

def setup_browser_menu(browser):
    menu = QMenu("LexiSage", browser)
    browser.form.menubar.addMenu(menu)
    action = QAction("批量生成释义", browser)
    action.triggered.connect(lambda: on_browser_batch_generate(browser))
    menu.addAction(action)
    menu.addSeparator()
    menu.addAction(QAction("设置...", browser, triggered=open_settings))

def on_browser_batch_generate(browser):
    config = load_config()
    selected_nids = browser.selectedNotes()
    if not selected_nids: return showInfo("请先选择笔记。")

    mw.app.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
    
    # --- 1. 预计算阶段：扫描所有选中笔记，统计状态 ---
    # 我们暂时不创建 Task 对象，而是存储元数据，以便用户决定后生成
    pre_scan_data = [] 
    
    stats = {
        "total_notes": len(selected_nids),
        "total_configured_fields": 0, # 总共涉及的配置字段数 (Update + Skip)
        "ready_to_update": 0,         # 当前为空，准备写入
        "skipped_not_empty": 0,       # 当前非空，默认跳过
        "skipped_not_configured": 0   # 笔记类型未配置
    }

    try:
        configs_cache = config.get("noteTypeConfigs", {})
        
        for nid in selected_nids:
            note = mw.col.get_note(nid)
            nt_name = note.note_type()["name"]
            
            if nt_name not in configs_cache:
                stats["skipped_not_configured"] += 1
                continue
                
            conf = configs_cache[nt_name]
            src = conf.get("fieldToExplain")
            ctx_field = conf.get("contextField")
            field_prompts = conf.get("fieldPrompts", {}) 
            
            # 检查源字段
            if not src or src not in note or is_field_visually_empty(note[src]):
                continue

            # 分类目标字段
            empty_fields_map = {}      # 准备更新 (空)
            non_empty_fields_map = {}  # 准备跳过 (非空)

            for target_field, prompt_tmpl in field_prompts.items():
                if target_field not in note: continue
                
                stats["total_configured_fields"] += 1
                
                if is_field_visually_empty(note[target_field]):
                    empty_fields_map[target_field] = prompt_tmpl
                    stats["ready_to_update"] += 1
                else:
                    non_empty_fields_map[target_field] = prompt_tmpl
                    stats["skipped_not_empty"] += 1
            
            # 只有当该笔记至少有一个配置的目标字段（无论空或非空）时，才记录
            if empty_fields_map or non_empty_fields_map:
                context_val = note[ctx_field] if ctx_field and ctx_field in note else ""
                
                pre_scan_data.append({
                    "nid": nid,
                    "word": note[src],
                    "context": context_val,
                    "empty_map": empty_fields_map,
                    "non_empty_map": non_empty_fields_map
                })

    finally:
        mw.app.restoreOverrideCursor()

    if not pre_scan_data:
        return showInfo(f"未找到可处理的任务。\n选中: {stats['total_notes']}\n未配置: {stats['skipped_not_configured']}")

    # --- 2. 构造高级确认弹窗 ---
    msg_box = QMessageBox(browser.window())
    msg_box.setWindowTitle("LexiSage 任务确认")
    msg_box.setIcon(QMessageBox.Icon.Question)
    
    text = (
        f"准备执行生成任务：\n"
        f"选中笔记数: {stats['total_notes']}\n"
        f"----------------------------------\n"
        f"包含字段总数: {stats['total_configured_fields']}\n"
        f"  ├─ 将更新字段数 (为空): {stats['ready_to_update']}\n"
        f"  └─ 将跳过字段数 (已有内容): {stats['skipped_not_empty']}\n\n"
        f"提示：如需写入“将跳过字段”，请点击【覆盖】。"
    )
    msg_box.setText(text)
    
    # 自定义按钮：提供覆盖、更新和取消三个选项，布局上使Update和Cancel靠近，Overwrite独立
    # 1. 添加覆盖按钮（独立放置）
    btn_overwrite = msg_box.addButton("覆盖 (Overwrite)", QMessageBox.ButtonRole.ActionRole)
    
    # 2. 添加更新按钮（默认选项）
    btn_update = msg_box.addButton("更新 (Update)", QMessageBox.ButtonRole.ActionRole)
    
    # 3. 添加取消按钮（拒绝角色）
    btn_cancel = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
    
    msg_box.setDefaultButton(btn_update)
    msg_box.setEscapeButton(btn_cancel)
    
    msg_box.exec()
    
    clicked_button = msg_box.clickedButton()

    # --- 3. 根据用户选择构建最终任务列表 ---
    final_tasks = []
    
    if clicked_button == btn_cancel:
        return # 用户取消
        
    is_overwrite_mode = (clicked_button == btn_overwrite)
    
    for item in pre_scan_data:
        target_map = {}
        
        if is_overwrite_mode:
            # 覆盖模式：合并空字段和非空字段
            target_map.update(item["empty_map"])
            target_map.update(item["non_empty_map"])
        else:
            # 更新模式：只使用空字段
            target_map.update(item["empty_map"])
            
        # 如果当前笔记有需要处理的字段，则创建任务
        if target_map:
            task = ExplanationTask(
                note_id=item["nid"],
                word=item["word"],
                context=item["context"],
                config=config,
                field_prompts_map=target_map
            )
            final_tasks.append(task)

    if not final_tasks:
        return showInfo("没有需要更新的字段 (所有字段均已有内容，且未选择覆盖)。")

    # --- 4. 启动 Worker ---
    # 此时 final_tasks 里的字段就是我们确定要写的，save_results 不需要再做空检查
    browser._lexisage_worker = BatchGenerationWorker(final_tasks, config)
    
    progress = QProgressDialog("启动引擎...", "取消", 0, len(final_tasks), browser.window())
    progress.setWindowTitle("LexiSage 执行中")
    progress.setMinimumDuration(0)
    progress.setAutoClose(False)

    def on_progress(c, t, w):
        progress.setValue(c)
        progress.setLabelText(f"处理中 ({c}/{t}): {w}")
        QApplication.processEvents()

    def on_finished(results):
        progress.close()
        save_results(results, browser)
        browser._lexisage_worker = None

    def on_error(err):
        progress.close()
        showInfo(f"错误: {err}")
        browser._lexisage_worker = None

    def on_cancel():
        if browser._lexisage_worker: browser._lexisage_worker.cancel()
        progress.close()

    browser._lexisage_worker.progress_signal.connect(on_progress)
    browser._lexisage_worker.finished_signal.connect(on_finished)
    browser._lexisage_worker.error_signal.connect(on_error)
    progress.canceled.connect(on_cancel)
    
    browser._lexisage_worker.start()
    progress.show()

def save_results(completed_tasks, browser):
    """
    将 Worker 返回的结果写回数据库。
    重要变更：不再检查 is_field_visually_empty。
    原因：任务生成前已经由用户确认了（更新模式只发了空字段，覆盖模式发了所有字段）。
    只要任务里有结果，就代表用户想写。
    """
    saved_fields = 0
    error_count = 0
    total_tokens = 0
    
    mw.col.db.execute("begin")
    try:
        for task in completed_tasks:
            if task.success and task.results_map:
                try:
                    note = mw.col.get_note(task.note_id)
                    total_tokens += task.tokens
                    
                    # 遍历返回的 JSON 字典，直接写入
                    for field, content in task.results_map.items():
                        if field in note:
                            note[field] = content
                            saved_fields += 1
                    note.flush()
                except Exception as e:
                    error_count += 1
                    # 记录具体错误以便调试
                    print(f"Error saving note {task.note_id}: {e}")
            else:
                error_count += 1
    except Exception as e:
        # 如果发生异常，回滚事务
        mw.col.db.execute("rollback")
        showInfo(f"保存数据时发生错误，事务已回滚: {e}", parent=browser.window())
        browser.model.reset()
        return
    else:
        # 如果没有异常，提交事务
        mw.col.db.execute("commit")
        
    browser.model.reset()
    showInfo(f"<h3>处理完成</h3><ul><li>填充/更新字段数: {saved_fields}</li><li>失败任务: {error_count}</li><li><b>Total Tokens: {total_tokens}</b></li></ul>", parent=browser.window(), title="LexiSage 报告", textFormat="rich")

# --- 编辑器单卡生成：在编辑单个卡片时生成释义 ---

def add_editor_button(buttons, editor):
    buttons.append(editor.addButton(icon=None, cmd="lexiSage", func=lambda e=editor: on_editor_gen(e), tip="LexiSage: 立即生成", label="LexiSage"))
    return buttons

def on_editor_gen(editor):
    config = load_config()
    note = editor.note
    nt_name = note.note_type()["name"]
    configs = config.get("noteTypeConfigs", {})
    
    if nt_name not in configs: 
        showInfo("当前笔记类型未在设置中配置。")
        return
    
    conf = configs[nt_name]
    src = conf.get("fieldToExplain")
    
    if not src or is_field_visually_empty(note[src]): 
        showInfo(f"源字段 '{src}' 为空或不存在。")
        return

    # 编辑器模式下，默认只处理空字段（为了安全，单卡如果要覆盖建议手动删掉再点）
    batch_fields = {}
    for target_field, prompt_template in conf.get("fieldPrompts", {}).items():
        if target_field in note and is_field_visually_empty(note[target_field]):
            batch_fields[target_field] = prompt_template
            
    if not batch_fields: 
        showInfo("没有检测到空的配置字段。如需重新生成，请先清空目标字段内容。")
        return

    progress_dialog = QProgressDialog("AI 思考中...", "取消", 0, 0, editor.parentWindow)
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setCancelButton(None) 
    progress_dialog.show()
    QApplication.processEvents()

    try:
        ctx_field_name = conf.get("contextField")
        context_val = ""
        if ctx_field_name and ctx_field_name in note:
            context_val = note[ctx_field_name]

        generated_results, tokens = generate_batch_explanation(
            word=note[src], 
            context=context_val,
            config=config,
            field_prompts_map=batch_fields
        )
        
        if generated_results:
            for field_name, field_content in generated_results.items():
                if field_name in note: 
                    note[field_name] = field_content
            note.flush()
            editor.loadNote() 
            tooltip(f"生成完成! 消耗 Tokens: {tokens}")
        else:
            showInfo("API 请求失败或解析错误，请检查日志。")
    except Exception as e:
        # 捕获所有异常，确保对话框关闭，并显示错误信息
        showInfo(f"生成释义时发生错误: {str(e)}")
    finally:
        progress_dialog.close()

# --- 注册入口：将功能添加到Anki的菜单和编辑器中 ---

# 1. 注册到 Tools 菜单
action = QAction("LexiSage设置...", mw)
action.triggered.connect(open_settings)
mw.form.menuTools.addAction(action)

# 2. 注册到 Editor 按钮
addHook("setupEditorButtons", add_editor_button)

# 3. 注册到 Browser 菜单
addHook("browser.setupMenus", setup_browser_menu)
