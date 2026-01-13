# LexiSage 开发指南

[中文](DEVELOPMENT.md) | [English](DEVELOPMENT_EN.md)

本文档提供了有关如何开发、构建和贡献LexiSage项目的详细信息。LexiSage是一个Anki插件，利用AI为语言学习者生成单词释义、同义词、语法说明和例句。

## 项目架构概述

LexiSage采用模块化设计，将不同功能分离到独立的Python文件中，便于维护和扩展。整个插件遵循MVC-like模式：
- **模型层**：`ai_service.py` 和 `prompts.py` 处理数据逻辑和AI交互
- **视图层**：`config_ui.py` 提供用户界面
- **控制器层**：`__init__.py` 作为入口点协调各模块工作

## 文件结构详解

### 1. `__init__.py` - 插件入口点
**核心功能**：插件的主要入口，负责注册Anki钩子、协调各个模块的工作。
**主要内容**：
- `BatchGenerationWorker`：后台线程类，用于批量生成释义，避免界面卡顿
- `save_results()`：将AI生成的结果写回Anki数据库，包含事务处理
- `on_browser_batch_generate()`：浏览器批量生成功能
- `on_editor_gen()`：编辑器单卡生成功能
- `setup_browser_menu()`：向Anki浏览器添加LexiSage菜单
- `add_editor_button()`：向编辑器添加LexiSage按钮
**关键特性**：
- 完整的异常处理和资源清理
- 数据库事务回滚机制，防止数据损坏
- 进度对话框管理，确保界面响应

### 2. `ai_service.py` - AI服务层
**核心功能**：封装与各种AI服务（OpenAI、XAI、DeepSeek）的通信逻辑。
**主要内容**：
- `generate_batch_explanation()`：核心函数，构建JSON payload并调用AI服务
- `ExplanationTask`：表示单个释义生成任务的类
- `ProgressTracker`：多线程进度跟踪器
- `generate_explanations_batch()`：批量处理多个任务的函数
- `format_text_to_html()`：清理AI返回文本的工具函数
**关键特性**：
- 支持多线程并发请求
- 完整的日志记录系统（lexisage.log）
- 自动重试机制（最大重试2次）
- 统一的API接口，支持多种AI服务

### 3. `config_ui.py` - 配置界面
**核心功能**：提供用户友好的配置界面，管理插件设置。
**主要内容**：
- `ConfigDialog`：主配置对话框类，包含三个标签页
- `NoteTypeConfig`：笔记类型配置的数据类
- 三个标签页：
  1. **笔记类型设置**：配置不同笔记类型的字段映射和提示词
  2. **AI系统指令**：设置全局AI系统提示词
  3. **AI服务设置**：配置API密钥、模型参数和高级选项
**关键特性**：
- 动态UI更新，实时预览AI发送内容
- 配置验证和错误处理
- 默认模板查看功能

### 4. `prompts.py` - 提示词管理
**核心功能**：集中管理所有AI提示词模板，提供默认配置。
**主要内容**：
- `DEFAULT_GLOBAL_SYSTEM_PROMPT`：全局系统提示词，定义AI角色和行为规范
- `DEFAULT_FIELD_PROMPT_TEMPLATE`：字段默认提示词，当字段未配置自定义提示词时使用
- `BATCH_INSTRUCTION_TEMPLATE`：UI预览模板，仅用于显示目的
**关键特性**：
- 清晰的三层提示词架构（系统层、指令层、预览层）
- 统一的字符串格式，支持变量替换（`{word}`, `{context}`）
- 遵循"费曼原则"，强调通俗易懂的解释

## 代码架构优势

1. **关注点分离**：UI逻辑、业务逻辑和AI通信逻辑分离到不同文件
2. **可扩展性**：易于添加新的AI服务或功能模块
3. **可维护性**：清晰的模块边界和职责划分
4. **错误处理**：全面的异常捕获和用户友好的错误提示
5. **配置管理**：统一的配置系统，支持多种笔记类型

## 未来重构建议

### 1. 进一步模块化
**建议**：将大型文件进一步拆分为更小的专用模块。
- 创建 `threading_utils.py`：集中管理多线程相关代码（`BatchGenerationWorker`, `ProgressTracker`）
- 创建 `database_utils.py`：处理所有数据库操作（`save_results`, 字段检查函数）
- 创建 `logging_utils.py`：统一日志记录和错误处理

### 2. 配置系统改进
**建议**：使用更结构化的配置管理。
- 引入配置验证和迁移工具
- 支持配置版本升级
- 添加配置导入/导出功能

### 3. 测试框架
**建议**：建立完整的测试套件。
- 单元测试：测试各个模块的核心功能
- 集成测试：测试模块间协作
- 端到端测试：模拟真实Anki环境下的使用场景

### 4. 国际化支持
**建议**：为多语言用户提供支持。
- 提取所有UI文本到翻译文件
- 支持动态语言切换
- 提供翻译贡献指南

## 开发环境设置

1. **克隆仓库**：
   ```bash
   git clone https://github.com/{你的用户名}/LexiSage.git
   cd LexiSage
   ```

2. **Python环境**：
   - 需要Python 3.8或更高版本
   - 建议使用虚拟环境：`python -m venv venv`
   - 激活虚拟环境：
     - Windows: `venv\Scripts\activate`
     - macOS/Linux: `source venv/bin/activate`

3. **依赖安装**：
   ```bash
   pip install requests
   # 其他依赖根据需求安装
   ```

4. **Anki开发环境**：
   - 将插件目录链接到Anki的addons21文件夹
   - 重启Anki加载插件
   - 使用Anki的开发工具进行调试

## 打包插件

1. **确保包含必要文件**：
   - `__init__.py`: 插件入口点
   - `ai_service.py`: AI服务接口
   - `config_ui.py`: 配置界面
   - `prompts.py`: 默认提示词
   - `manifest.json`: 插件元数据，包含名称、版本等信息
   - `meta.json`: Anki版本兼容性信息（重要，决定支持的Anki版本）
   - `config.json`: 默认配置（可选）
   - `LICENSE`: 许可证文件（GNU通用公共许可证v3.0）

2. **更新版本号**：
   - 在`manifest.json`中更新`version`字段
   - 在`ankiweb.json`中同步版本号

3. **打包命令**：
   ```bash
   zip -r LexiSage.ankiaddon __init__.py ai_service.py config_ui.py prompts.py manifest.json meta.json LICENSE -x ".*" "__pycache__/*" "*.pyc"
   ```

4. **验证打包内容**：
   ```bash
   unzip -l LexiSage.ankiaddon
   ```
   确保不包含`.git`、`__pycache__`等多余文件。

## 提交到AnkiWeb

1. 注册[AnkiWeb账户](https://ankiweb.net/account/register)
2. 登录后访问[共享页面](https://ankiweb.net/shared/info/)
3. 点击"Upload Add-on"提交插件
4. 填写插件信息并上传打包文件
5. 等待审核通过

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！

1. **Fork仓库**：在GitHub上fork此仓库
2. **创建分支**：`git checkout -b feature/your-feature-name`
3. **提交更改**：`git commit -m 'Add some feature'`
4. **推送分支**：`git push origin feature/your-feature-name`
5. **创建PR**：在GitHub上创建Pull Request

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 确保新功能有相应的错误处理
- 更新相关文档

### 测试要求
- 新功能应包含测试用例
- 确保现有测试通过
- 更新测试文档

## 故障排除

### 常见问题
1. **AI服务连接失败**：检查API密钥和网络连接
2. **配置保存失败**：检查文件权限和磁盘空间
3. **UI显示异常**：重启Anki或清除缓存

### 调试技巧
1. **查看日志文件**：在运行过一次填充字段后，`lexisage.log`记录了所有API请求和错误
2. **简化配置**：从最小配置开始，逐步添加复杂功能

## 许可证

本项目采用GNU通用公共许可证v3.0 (GPL-3.0)。详情请参阅[LICENSE](LICENSE)文件。

---

*最后更新：2026年1月*
*版本：基于LexiSage当前架构的分析和优化建议*
