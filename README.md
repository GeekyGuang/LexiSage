# LexiSage - Anki智能释义插件

> LexiSage – Let your cards speak with clarity and wisdom.

<img src="screenshot.png" alt="LexiSage截图" width="600"/>

## 项目简介
LexiSage是一款为Anki设计的智能释义插件，支持调用多种AI接口（OpenAI、XAI、DeepSeek）对选定字段进行解释，特别适合语言学习者。

### 主要功能
- 支持多种AI服务（OpenAI、XAI、DeepSeek）
- 自动解析词语含义和用法
- 支持根据上下文解释单词
- 批量处理功能，提高学习效率
- 可自定义系统提示词
- 支持多笔记类型配置

## 安装说明

### 方法1：通过AnkiWeb（推荐）
1. 在Anki中，点击"工具">"插件"
2. 点击"获取插件"
3. 输入插件代码：`[发布后填写AnkiWeb插件ID]`
4. 重启Anki

### 方法2：手动安装
1. 下载此仓库的ZIP文件
2. 解压到Anki的插件目录：
   - Windows: `%APPDATA%\Anki2\addons21\`
   - Mac: `~/Library/Application Support/Anki2/addons21/`
   - Linux: `~/.local/share/Anki2/addons21/`
3. 重命名文件夹为`anki_lexisage`
4. 重启Anki

## 使用说明

### 基本配置
1. 打开Anki，在工具菜单中选择"LexiSage 设置..."
2. 在"基本设置"选项卡中：
   - 添加需要处理的笔记类型配置
   - 选择要解释的字段
   - 选择上下文字段（可选）
   - 选择释义目标字段
   - 自定义系统提示词（可选）
3. 在"AI服务设置"选项卡中：
   - 选择要使用的AI服务
   - 输入相应的API配置信息

### 释义生成
1. **单条笔记释义**：在编辑器中点击"LexiSage"按钮
2. **批量生成释义**：在浏览器中选择多条笔记，然后点击LexiSage菜单中的"批量生成释义"

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
1. 确保项目结构正确
2. 创建`manifest.json`和`ankiweb.json`文件
3. 使用zip打包，确保不包含`.git`、`__pycache__`等非必要文件
4. 可以使用以下命令打包：`zip -r anki_lexisage.ankiaddon * -x ".*" "__pycache__/*" "*.pyc"`

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
