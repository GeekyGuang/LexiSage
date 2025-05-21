import json
import requests
import time
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
            print(f"正在调用DeepSeek API, URL: {api_config['baseUrl']}")
            print(f"请求数据: {data}")

            response = requests.post(
                api_config["baseUrl"],
                headers=headers,
                json=data,  # 使用json参数而不是data+json.dumps
                timeout=45  # 增加超时时间
            )

            # 打印调试信息
            print(f"DeepSeek API响应状态码: {response.status_code}")
            print(f"DeepSeek API响应内容: {response.text[:200]}...")  # 打印前200个字符

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

        # 调试信息
        print(f"[LexiSage Debug] 使用有上下文提示词")
        print(f"[LexiSage Debug] 使用自定义提示词: {bool(custom_with_context)}")

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

        # 调试信息
        print(f"[LexiSage Debug] 使用无上下文提示词")
        print(f"[LexiSage Debug] 使用自定义提示词: {bool(custom_no_context)}")

    # 将提示词和所选提示词类型记录到日志，以便调试
    print(f"[LexiSage Debug] 使用的系统提示词内容: {system_prompt[:50]}...")
    print(f"[LexiSage Debug] 使用的用户提示词内容: {user_prompt}")

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
