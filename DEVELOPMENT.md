# LexiSage 开发指南

[中文](DEVELOPMENT.md) | [English](DEVELOPMENT_EN.md)

本文档提供了有关如何开发、构建和贡献LexiSage项目的详细信息。

## 环境设置
1. 克隆此仓库
2. 确保您已安装Python 3.8+
3. 安装依赖：`pip install -r requirements.txt`（如果有）

## 项目结构
- `__init__.py`: 插件入口点和主要功能
- `config_ui.py`: 配置UI界面
- `ai_service.py`: AI服务调用接口
- `prompts.py`: 默认提示词模板

## 打包插件
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

## 提交到AnkiWeb
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
