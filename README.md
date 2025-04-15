# LexiSage - Anki智能释义插件

[English](README_EN.md) | 中文

> LexiSage – Let your cards speak with clarity and wisdom.

## 项目简介
[LexiSage](https://ankiweb.net/shared/info/750479332?cb=1744698675805)是一款为Anki设计的智能释义插件，支持调用多种AI接口（OpenAI、XAI、DeepSeek）对选定字段进行解释，特别适合语言学习者。

### 主要功能
- 自动解析词语含义和用法
- 支持根据上下文解释单词
- 批量处理功能，提高学习效率
- 支持多种AI服务，需自备 API Key

## 安装说明

1. 在Anki中，点击"工具">"插件"
2. 点击"获取插件"
3. 输入插件代码：**750479332**
4. 重启Anki

## 使用说明

### 基本配置

1. 打开Anki，在"工具"菜单中选择"LexiSage 设置..."
2. 设置 AI 服务。

   插件本身不提供 AI 服务，需要用户自行购买 AI 服务商的 API Key 填入插件中，在获得 API Key 之后，选择对应的服务商，填写正确的 API Key 和要使用的模型。

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
3. 点击菜单栏"LexiSage"-"批量生成释义"，等待完成

   ![image](https://github.com/user-attachments/assets/6ebbb32e-e9a9-4f84-96d1-cc05041e3b8c)

### 自定义 Prompt

本插件内置了 Prompt，如果你对释义的结果不满意，可以在"LexiSage 设置"中自定义提示词

## 开发者指南

如果你想了解项目结构，构建流程，或者想要参与贡献，请查看我们的[开发者文档](DEVELOPMENT.md)。

## 许可证
本项目采用 [GNU通用公共许可证v3.0(GPL-3.0)](LICENSE) - 详情请参阅LICENSE文件。

## 致谢
- 感谢所有贡献者和用户
- 特别感谢Anki开发团队提供的优秀平台

## 隐私说明
此插件会将您的卡片内容发送到您配置的AI服务，请确保您了解相关隐私政策。API密钥仅存储在本地配置文件中，不会被上传。
