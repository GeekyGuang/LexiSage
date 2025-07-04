import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from aqt.utils import showInfo
from urllib.error import URLError, HTTPError
from .prompts import DEFAULT_NO_CONTEXT_PROMPT, DEFAULT_WITH_CONTEXT_PROMPT

# OpenAI API调用
def call_openai_api(prompt, config, system_prompt=None):
    api_config = config["apiConfig"]["openai"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['apiKey']}"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": api_config["model"],
        "messages": messages,
        "temperature": 0.7
    }

    # 添加错误提示信息
    error_tips = """
可能的解决方法:
1. 检查您的网络连接是否稳定
2. 确认API密钥是否有效
3. 确认模型名称是否正确
4. 如果使用代理，请检查代理设置
5. 尝试更换API服务地址(如使用自定义API)
"""

    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.post(
                f"{api_config['baseUrl']}/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=45  # 增加超时时间
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.SSLError as e:
            error_message = f"OpenAI API调用失败 (SSL错误): {str(e)}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)  # 等待1秒后重试
        except (HTTPError, URLError) as e:
            error_message = f"OpenAI API调用失败 (HTTP错误): {str(e)}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except requests.RequestException as e:
            error_message = f"OpenAI API调用失败 (请求错误): {str(e)}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except Exception as e:
            showInfo(f"OpenAI API调用失败 (未知错误): {str(e)}\n{error_tips}")
            return None

# XAI API调用
def call_xai_api(prompt, config, system_prompt=None):
    api_config = config["apiConfig"]["xai"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['apiKey']}"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": api_config["model"],
        "messages": messages,
        "temperature": 0.7
    }

    # 添加错误提示信息
    error_tips = """
可能的解决方法:
1. 检查您的网络连接是否稳定
2. 确认API URL是否正确 - XAI需要完整的URL，包含/v1/chat/completions路径
   示例: https://api.x.ai/v1/chat/completions
3. 确认API密钥是否有效
4. 如果使用代理，请检查代理设置
5. 尝试使用其他AI服务提供商
"""

    max_retries = 2
    retry_count = 0

    # 检查并修正URL格式
    base_url = api_config['baseUrl']

    while retry_count <= max_retries:
        try:
            # 增加超时时间
            response = requests.post(
                base_url,
                headers=headers,
                data=json.dumps(data),
                timeout=45  # 增加超时时间
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.SSLError as e:
            error_message = f"XAI API调用失败 (SSL错误): {str(e)}\n当前URL: {base_url}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)  # 等待1秒后重试
        except (HTTPError, URLError) as e:
            error_message = f"XAI API调用失败 (HTTP错误): {str(e)}\n当前URL: {base_url}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except requests.RequestException as e:
            error_message = f"XAI API调用失败 (请求错误): {str(e)}\n当前URL: {base_url}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except Exception as e:
            showInfo(f"XAI API调用失败 (未知错误): {str(e)}\n当前URL: {base_url}\n{error_tips}")
            return None

# DeepSeek API调用
def call_deepseek_api(prompt, config, system_prompt=None):
    api_config = config["apiConfig"]["deepseek"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['apiKey']}"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": api_config["model"],
        "messages": messages,
        "temperature": 0.7
    }

    # 添加错误提示信息
    error_tips = """
可能的解决方法:
1. 检查您的网络连接是否稳定
2. 确认API URL是否正确 (应包含完整路径)
3. 确认API密钥是否有效
4. 如果使用代理，请检查代理设置
5. 尝试使用其他AI服务提供商
"""

    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # 增加超时时间并使用json参数替代data参数
            response = requests.post(
                api_config["baseUrl"],
                headers=headers,
                json=data,  # 使用json参数而不是data+json.dumps
                timeout=45  # 增加超时时间
            )

            response.raise_for_status()
            result = response.json()

            # 适应不同的响应格式
            try:
                return result["choices"][0]["message"]["content"].strip()
            except KeyError:
                # 如果响应格式不同，尝试其他可能的格式
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "text" in choice:
                        return choice["text"].strip()
                    elif "content" in choice:
                        return choice["content"].strip()

                # 如果无法解析响应，返回错误
                error_msg = f"无法解析DeepSeek API响应: {str(result)[:200]}..."
                showInfo(error_msg)
                return None

        except requests.exceptions.SSLError as e:
            error_message = f"DeepSeek API调用失败 (SSL错误): {str(e)}\nURL: {api_config['baseUrl']}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)  # 等待1秒后重试
        except (HTTPError, URLError) as e:
            error_message = f"DeepSeek API调用失败 (HTTP错误): {str(e)}\nURL: {api_config['baseUrl']}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except requests.RequestException as e:
            error_message = f"DeepSeek API调用失败 (请求错误): {str(e)}\nURL: {api_config['baseUrl']}\n{error_tips}"
            if retry_count == max_retries:
                showInfo(error_message)
                return None
            retry_count += 1
            time.sleep(1)
        except Exception as e:
            showInfo(f"DeepSeek API调用失败 (未知错误): {str(e)}\nURL: {api_config['baseUrl']}\n{error_tips}")
            return None

# 根据配置选择合适的API并生成释义
def generate_explanation(word, context, config):
    # 首先确定是否有上下文
    has_context = bool(context and context.strip())

    if has_context:
        # 有上下文的情况
        # 始终使用 withContextSystemPrompt 配置项
        custom_with_context = config.get("withContextSystemPrompt", "").strip()

        # 如果用户设置了自定义有上下文提示词，使用它
        if custom_with_context:
            system_prompt = custom_with_context
        else:
            system_prompt = DEFAULT_WITH_CONTEXT_PROMPT

        user_prompt = f"请讲解词语或短语「{word}」在「{context}」中的用法和含义。"

    else:
        # 无上下文的情况
        # 始终使用 noContextSystemPrompt 配置项
        custom_no_context = config.get("noContextSystemPrompt", "").strip()

        # 如果用户设置了自定义无上下文提示词，使用它
        if custom_no_context:
            system_prompt = custom_no_context
        else:
            system_prompt = DEFAULT_NO_CONTEXT_PROMPT

        user_prompt = f"请讲解「{word}」"

    # 根据配置选择AI服务
    ai_service = config.get("aiService", "openai")

    if ai_service == "openai":
        return call_openai_api(user_prompt, config, system_prompt)
    elif ai_service == "xai":
        return call_xai_api(user_prompt, config, system_prompt)
    elif ai_service == "deepseek":
        return call_deepseek_api(user_prompt, config, system_prompt)
    else:
        showInfo(f"不支持的AI服务: {ai_service}")
        return None

# 多线程批量生成释义的任务类
class ExplanationTask:
    def __init__(self, note_id, word, context, config, note_type_config):
        self.note_id = note_id
        self.word = word
        self.context = context
        self.config = config
        self.note_type_config = note_type_config
        self.result = None
        self.error = None
        self.success = False

# 用于线程安全的进度更新
class ProgressTracker:
    def __init__(self):
        self.lock = Lock()
        self.completed = 0
        self.total = 0
        self.current_word = ""

    def update_progress(self, word=""):
        with self.lock:
            self.completed += 1
            if word:
                self.current_word = word

    def get_progress(self):
        with self.lock:
            return self.completed, self.total, self.current_word

    def set_total(self, total):
        with self.lock:
            self.total = total

# 单个任务的处理函数
def process_single_explanation(task, progress_tracker):
    """处理单个释义生成任务"""
    try:
        # 更新进度跟踪器
        progress_tracker.update_progress(task.word)

        # 生成释义
        explanation = generate_explanation(task.word, task.context, task.config)

        if explanation:
            # 将纯文本换行转换为HTML换行标签
            task.result = explanation.replace("\n", "<br>")
            task.success = True
        else:
            task.error = "API调用失败"
            task.success = False

    except Exception as e:
        task.error = str(e)
        task.success = False

    return task

# 多线程批量生成释义
def generate_explanations_batch(tasks, max_workers=3, progress_callback=None):
    """
    批量生成释义，使用多线程

    Args:
        tasks: ExplanationTask对象列表
        max_workers: 最大并发线程数
        progress_callback: 进度回调函数，接收(completed, total, current_word)参数

    Returns:
        处理完成的任务列表
    """
    if not tasks:
        return []

    # 创建进度跟踪器
    progress_tracker = ProgressTracker()
    progress_tracker.set_total(len(tasks))

    completed_tasks = []

    # 使用线程池处理任务
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(process_single_explanation, task, progress_tracker): task
            for task in tasks
        }

        # 处理完成的任务
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                # 获取任务结果
                completed_task = future.result()
                completed_tasks.append(completed_task)

                # 如果有进度回调，调用它
                if progress_callback:
                    completed, total, current_word = progress_tracker.get_progress()
                    progress_callback(completed, total, current_word)

            except Exception as e:
                # 处理任务执行过程中的异常
                task.error = str(e)
                task.success = False
                completed_tasks.append(task)

                if progress_callback:
                    completed, total, current_word = progress_tracker.get_progress()
                    progress_callback(completed, total, current_word)

    return completed_tasks
