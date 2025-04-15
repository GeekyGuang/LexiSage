# LexiSage - Anki智能释义插件

> LexiSage – Let your cards speak with clarity and wisdom.

## 项目简介
[LexiSage](https://ankiweb.net/shared/info/750479332?cb=1744698675805)是一款为Anki设计的智能释义插件，支持调用多种AI接口（OpenAI、XAI、DeepSeek）对选定字段进行解释，特别适合语言学习者。

### 主要功能
- 支持多种AI服务（OpenAI、XAI、DeepSeek）
- 自动解析词语含义和用法
- 支持根据上下文解释单词
- 批量处理功能，提高学习效率
- 可自定义系统提示词
- 支持多笔记类型配置

## 安装说明

1. 在Anki中，点击"工具">"插件"
2. 点击"获取插件"
3. 输入插件代码：**750479332**
4. 重启Anki

## 使用说明

### 基本配置

1. 打开Anki，在“工具”菜单中选择"LexiSage 设置..."
2. 设置 AI 服务。插件本身不提供 AI 服务，需要用户自行购买 AI 服务商的 API Key 填入插件中，在获得 API Key 之后，选择对应的服务商，填写正确的 API Key 和要使用的模型。
   AI 服务商推荐
   - [xAI](https://console.x.ai)(充 5 刀每个月送 150 刀，很划算)
   - [DeepSeek](https://platform.deepseek.com)(国产 AI 之光)
   
   ![image](https://github.com/user-attachments/assets/1d33d54d-ca04-4507-83bd-84267557fb0a)
3. 为你的笔记类型添加配置，指定模板中要 AI 解释的字段，指定存放输出结果的字段，还可以为单词指定上下文，根据上下文来释义。
  
   ![image](https://github.com/user-attachments/assets/ca6f59d6-ab80-4911-b6e0-24c5f3fa0e49)
   
   - 点 + 号添加笔记类型配置
   - 选择要解释的字段
   - 选择上下文字段（可选）
   - 选择释义目标字段
   - 保存配置
   （本插件支持配置多个笔记类型，在批量生成释义时即使选择了不同类型的笔记也能一并处理）

### 释义生成

1. 浏览牌组
2. 选择要生成释义卡片
3. 点击菜单栏“LexiSage”-“批量生成释义”，等待完成
  
   ![image](https://github.com/user-attachments/assets/6ebbb32e-e9a9-4f84-96d1-cc05041e3b8c)

### 自定义 Prompt

本插件内置了 Prompt，如果你对释义的结果不满意，可以在“LexiSage 设置”中自定义提示词

## 开发指南

### 环境设置
1. 克隆此仓库
2. 确保您已安装Python 3.8+
3. 安装依赖：`pip install -r requirements.txt`（如果有）

### 项目结构
- `__init__.py`: 插件入口点和主要功能
- `config_ui.py`: 配置UI界面
- `ai_service.py`: AI服务调用接口
- `prompts.py`: 默认提示词模板

### 打包插件
1. 确保项目包含以下必要文件:
   - `__init__.py`: 插件入口点
   - `ai_service.py`: AI服务接口
   - `config_ui.py`: 配置界面
   - `prompts.py`: 默认提示词
   - `manifest.json`: 插件元数据，包含名称、版本等信息
   - `meta.json`: Anki版本兼容性信息(重要，决定支持的Anki版本)
   - `config.json`: 默认配置(可选)
   - `LICENSE`: 许可证文件

2. 更新版本号:
   - 在`manifest.json`文件中更新`version`字段
   - 在`ankiweb.json`文件中同步更新版本号(用于提交到AnkiWeb)

3. 使用以下命令打包:
   ```bash
   zip -r anki_lexisage.ankiaddon __init__.py ai_service.py config_ui.py prompts.py manifest.json meta.json LICENSE config.json -x ".*" "__pycache__/*" "*.pyc"
   ```

4. 验证打包内容:
   ```bash
   unzip -l anki_lexisage.ankiaddon
   ```
   确保只包含必要文件，没有多余的`.git`、`__pycache__`等文件

5. 测试安装:
   - 在测试环境中通过Anki的"从文件安装插件"功能安装`.ankiaddon`文件
   - 验证插件功能是否正常运行

### 提交到AnkiWeb
1. 注册[AnkiWeb账户](https://ankiweb.net/account/register)
2. 登录后，访问[共享页面](https://ankiweb.net/shared/info/)
3. 点击"Upload Add-on"提交你的插件
4. 填写插件信息并上传打包好的文件
5. 等待审核通过

## 贡献指南
欢迎贡献代码、报告问题或提出新功能建议！

1. Fork此仓库
2. 创建您的特性分支: `git checkout -b feature/amazing-feature`
3. 提交您的更改: `git commit -m '添加了一些很棒的功能'`
4. 推送到分支: `git push origin feature/amazing-feature`
5. 开启一个Pull Request

## 许可证
本项目采用 [MIT许可证](LICENSE) - 详情请参阅LICENSE文件。

## 致谢
- 感谢所有贡献者和用户
- 特别感谢Anki开发团队提供的优秀平台

## 支持的AI服务
- **OpenAI**：支持GPT-3.5/GPT-4等模型
- **XAI**：支持自定义API接口
- **DeepSeek**：支持DeepSeek Chat模型

## 自定义提示词
在提示词模板中，可以使用以下变量：
- `{word}`：代表要解释的字段内容
- `{context}`：代表上下文字段内容（如果有）

## 故障排除
- 如果插件无法正常工作，请检查：
  - API密钥是否正确
  - 网络连接是否正常
  - 是否选择了正确的字段
- 如遇到问题，可尝试重启Anki

## 隐私说明
此插件会将您的卡片内容发送到您配置的AI服务，请确保您了解相关隐私政策。API密钥仅存储在本地配置文件中，不会被上传。
