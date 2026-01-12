import json
import requests
import time
import re
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.error import URLError, HTTPError
from .prompts import DEFAULT_GLOBAL_SYSTEM_PROMPT, DEFAULT_FIELD_PROMPT_TEMPLATE

# --- 日志记录功能：记录API请求和响应以便调试 ---
def _write_log(service_name, url, request_payload, response_content=None, error_msg=None):
    try:
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(addon_dir, "lexisage.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_payload = request_payload.copy() if isinstance(request_payload, dict) else str(request_payload)
        
        log_entry = [
            f"{'='*60}",
            f"TIME: {timestamp}",
            f"SERVICE: {service_name}",
            f"URL: {url}",
            f"{'-'*20} REQUEST PAYLOAD {'-'*20}",
            json.dumps(safe_payload, ensure_ascii=False, indent=2),
            f"{'-'*20} RESPONSE / ERROR {'-'*20}"
        ]
        if error_msg:
            log_entry.append(f"ERROR: {error_msg}")
        else:
            log_entry.append(str(response_content))
        log_entry.append(f"{'='*60}\n")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n".join(log_entry))
    except Exception as e:
        print(f"Logging Failed: {e}")

# --- HTML/Text 清洗功能：将AI返回的文本转换为HTML格式并清理标记 ---
def format_text_to_html(text):
    if not text: return ""
    # 移除可能残留的 Markdown 代码块标记
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```json', '', text, flags=re.IGNORECASE)
    text = text.replace('```', '')
    
    # 注意：AI返回的内容已经是HTML格式（包含<b>、<br>等标签）
    # 因此我们不再进行Markdown到HTML的转换，以免破坏现有HTML标签
    # 只需清理代码块标记并返回原始文本
    
    return text.strip()

# --- API 底层调用功能：执行HTTP请求并处理重试和错误 ---
def _execute_request(url, headers, data, service_name):
    max_retries = 2
    retry_count = 0
    while retry_count <= max_retries:
        try:
            time.sleep(0.05) 
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            # 记录原始响应以便 Debug
            try:
                _write_log(service_name, url, data, response_content=json.dumps(response.json(), ensure_ascii=False, indent=2))
            except:
                _write_log(service_name, url, data, response_content=response.text)

            response.raise_for_status()
            result = response.json()
            
            usage = result.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            content = ""
            try:
                content = result["choices"][0]["message"]["content"].strip()
            except KeyError:
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    content = choice.get("text", "") or choice.get("content", "")
            
            if content:
                return content, total_tokens
            retry_count += 1
        except Exception as e:
            _write_log(service_name, url, data, error_msg=str(e))
            if retry_count == max_retries: return None, 0
            retry_count += 1
            time.sleep(1)
    return None, 0

def call_ai_service(user_content, config, system_content):
    service = config.get("aiService", "openai")
    api_config = config["apiConfig"].get(service, {})
    
    if not api_config.get("apiKey"): return None, 0

    temperature = api_config.get("temperature", 0.1)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_config['apiKey']}"}
    
    # 这里的 user_content 已经是一个 JSON 字符串，符合我们定义的 Protocol
    messages = [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]
    
    data = {"model": api_config["model"], "messages": messages, "temperature": temperature}
    
    svc_name_map = {"openai": "OpenAI", "xai": "XAI", "deepseek": "DeepSeek"}
    return _execute_request(api_config['baseUrl'], headers, data, svc_name_map.get(service, "Unknown"))


# --- 聚合生成逻辑：构建JSON payload发送给AI并解析返回结果 ---

def generate_batch_explanation(word, context, config, field_prompts_map):
    """
    构造 JSON Payload 发送给 AI，并解析返回的 JSON。
    """
    # 1. 获取系统提示词（协议层）
    system_prompt = config.get("globalSystemPrompt", "").strip() or DEFAULT_GLOBAL_SYSTEM_PROMPT
    
    safe_context = context if context else ""
    
    # 2. 构建需求字典（指令层）：遍历字段提示词映射，处理每个字段的特定提示
    requirements = {}

    for field, prompt in field_prompts_map.items():
        # 如果有自定义提示词则使用自定义，否则使用默认提示词
        if prompt and prompt.strip():
            p_text = prompt
        else:
            p_text = DEFAULT_FIELD_PROMPT_TEMPLATE
        
        # 在字段提示词中替换变量 {word} 和 {context}
        p_text = p_text.replace("{word}", word).replace("{context}", safe_context)
        requirements[field] = p_text

    # 3. 组装最终的用户负载数据
    user_payload = {
        "word": word,
        "context": safe_context,
        "requirements": requirements
    }

    # 4. 序列化为JSON字符串
    user_content_str = json.dumps(user_payload, ensure_ascii=False)

    # 5. 调用AI服务
    raw_content, tokens = call_ai_service(user_content_str, config, system_prompt)
    
    if not raw_content:
        return {}, 0

    # 6. 解析AI返回的JSON数据
    # 清洗可能包含的Markdown代码块标记
    clean_json_str = raw_content.replace("```json", "").replace("```", "").strip()
    
    results = {}
    try:
        results = json.loads(clean_json_str)
        
        # 将AI生成的内容转换为HTML格式
        for k, v in results.items():
            results[k] = format_text_to_html(str(v))
            
    except json.JSONDecodeError:
        _write_log("JSON_PARSE_ERROR", "Internal", raw_content, error_msg="AI did not return valid JSON")
        return None, tokens

    return results, tokens


# --- 任务类：表示单个释义生成任务，包含任务数据和结果 ---

class ExplanationTask:
    def __init__(self, note_id, word, context, config, field_prompts_map):
        self.note_id = note_id
        self.word = word
        self.context = context
        self.config = config
        self.field_prompts_map = field_prompts_map 
        self.results_map = {} 
        self.tokens = 0
        self.error = None
        self.success = False

# --- 进度跟踪器类：用于多线程环境中跟踪任务进度 ---

class ProgressTracker:
    def __init__(self):
        self.lock = Lock()
        self.completed = 0
        self.total = 0
        self.current_word = ""
    def update_progress(self, word=""):
        with self.lock:
            self.completed += 1
            if word: self.current_word = word
    def get_progress(self):
        with self.lock: return self.completed, self.total, self.current_word
    def set_total(self, total):
        with self.lock: self.total = total

# --- 单个任务处理函数：在独立线程中处理单个释义生成任务 ---

def process_single_task(task, progress_tracker):
    try:
        time.sleep(0.1)
        progress_tracker.update_progress(task.word)
        
        results, tokens = generate_batch_explanation(
            task.word, 
            task.context, 
            task.config, 
            task.field_prompts_map
        )
        
        if results is not None:
            task.results_map = results
            task.tokens = tokens
            task.success = True
        else:
            task.error = "JSON解析失败或API错误"
            task.success = False
            
    except Exception as e:
        task.error = str(e)
        task.success = False
    return task

# --- 批量生成函数：使用线程池并发处理多个释义生成任务 ---

def generate_explanations_batch(tasks, max_workers=3, progress_callback=None):
    if not tasks: return []
    
    progress_tracker = ProgressTracker()
    progress_tracker.set_total(len(tasks))
    
    completed_task_list = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(process_single_task, task, progress_tracker): task
            for task in tasks
        }
        
        for future in as_completed(future_to_task):
            time.sleep(0.01)
            task = future_to_task[future]
            
            try:
                processed_task = future.result()
                completed_task_list.append(processed_task)
            except Exception as e:
                task.error = str(e)
                completed_task_list.append(task)
            
            if progress_callback:
                completed_count, total_count, current_processing_word = progress_tracker.get_progress()
                progress_callback(completed_count, total_count, current_processing_word)
                
    return completed_task_list
