# LexiSage - Anki Smart Explanation Add-on

[English](README_EN.md) | [中文](README.md)

> LexiSage – Make your cards clear and intelligent

## 📖 Project Introduction

[LexiSage](https://ankiweb.net/shared/info/750479332?cb=1744698675805) is an intelligent explanation add-on for Anki that supports calling multiple AI interfaces (OpenAI, XAI, DeepSeek) to explain selected fields, especially suitable for language learners.

### ✨ Main Features

- **Automatic parsing of word meanings and usage**: AI intelligently analyzes the core meaning of words/phrases
- **Context-aware explanations**: Provide precise explanations based on example sentence context
- **Efficient batch processing**: Process multiple card fields at once, improving learning efficiency
- **Multi-AI service support**: Supports OpenAI, XAI, DeepSeek (requires your own API Key)
- **Independent multi-field configuration**: Each target field can have its own AI instructions

## 📦 Installation Instructions

### Simple Installation Steps

1. In Anki, click the top menu bar **Tools** → **Add-ons**
2. Click the **Get Add-ons...** button
3. Enter the add-on code: **750479332**
4. Click **OK** and restart Anki

---

## 🚀 Quick Start Guide

### Step 1: AI Service Configuration (Required for first use)

#### 1. Open the settings interface
- In the Anki main interface, click the top menu bar **Tools** → **LexiSage Settings...**

<p align="center">
  <img src="https://github.com/user-attachments/assets/1b28afbc-3d03-47b4-9c09-c3401b5d64bb" alt="LexiSage Settings Entry" width="600"/>
</p>

#### 2. Configure AI service
- Click the **3. AI Service Settings** tab at the top
- Choose your service provider:
  - [OpenAI](https://platform.openai.com/) (International mainstream)
  - [DeepSeek](https://platform.deepseek.com) (Cost‑effective AI)
  - [xAI](https://console.x.ai) (Grok model)

#### 3. Fill in API information
- **Base URL**: Usually use the default value
- **API Key**: Enter your service provider's API key (stored locally only)
- **Model selection**: Choose an appropriate model as needed
- **Advanced settings**: Can enable "Multi-threading concurrency" to accelerate batch generation

<p align="center">
  <img src="https://github.com/user-attachments/assets/60a69b10-8a52-47d2-92bb-ae173efd329d" alt="AI Service Settings Interface" width="600"/>
</p>

#### 4. Save configuration
- Click the **Save Configuration** button at the bottom

> ⚠️ **Important Note**: The add-on itself does not provide AI services, users need to purchase API Keys from AI service providers themselves. Please ensure you select the correct service provider and fill in a valid API Key.

---

### Step 2: Note Type and Field Mapping Configuration (Core Functionality)

#### 1. Add note type
- Switch to the **1. Note Type Settings** tab
- Find your card template in the left dropdown (such as `LexiSage Master` or `Basic`)
- Click the **↓ Add to Configuration List** button

#### 2. Configure source fields
- In the right panel, select **Source Word Field** (tells AI which word to explain, e.g., `Word`)
- (Recommended) Select **Source Context Field** (e.g., `Context`), allowing AI to provide precise explanations based on example sentences

#### 3. Configure target fields (Multi-field mapping)
- In the "Explanation Target Fields and Prompts" area:
  - Dropdown select the field to fill (e.g., `Meaning`)
  - Click the **+** button to add the field
  - Enter dedicated prompts in the text box (leave empty to use default prompts)
- Repeat the above steps to add all fields that need AI filling

<p align="center">
  <img src="https://github.com/user-attachments/assets/a56f25d2-571f-4e76-80bd-6a386332dcba" alt="Field Mapping Configuration" width="600"/>
</p>

#### 4. Preview and verify
- Return to the **3. AI Service Settings** tab
- First click **Save Configuration**
- Then click **🔍 Preview Complete Sending Content** to confirm the instructions received by AI meet expectations

---

### Step 3: Batch Generate Explanations (Daily Use)

#### 1. Select cards
- Open Anki's **Browse** interface
- Select the cards to process (multiple selection supported)

#### 2. Trigger generation
- Click the top menu bar **LexiSage** → **Batch Generate Explanations**

<p align="center">
  <img src="https://github.com/user-attachments/assets/fb44c4c6-d234-4af8-a9f5-49b9f799c272" alt="Batch Generation Menu" width="600"/>
</p>

#### 3. Choose processing mode
- **Update mode**: Only fills empty fields, absolutely safe, will not overwrite manual content
- **Overwrite mode**: Forces rewriting all selected fields, suitable for card revisions

#### 4. Wait for completion
- Progress bar shows processing progress
- After completion, displays token consumption and success statistics

---

### Step 4: Single Card Instant Generation (Learn and Modify)

#### 1. Open edit interface
- Use when adding new cards or editing existing cards

#### 2. Click generation button
- Click the **LexiSage** button on the editor toolbar

#### 3. Auto-fill
- The add-on automatically fills all empty fields according to configuration rules

<p align="center">
  <img src="https://github.com/user-attachments/assets/353e38be-8bf2-423c-a09b-1648a26e2673" alt="Single Card Generation Button" width="600"/>
</p>

---

## 👨‍💻 Developer Guide

If you want to understand the project structure, build process, or want to contribute, please check our [Development Documentation](DEVELOPMENT_EN.md).

## 📄 License

This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE) - see the LICENSE file for details.

## 📝 Changelog

Latest updates can be viewed via [Changelog](CHANGELOG.md).

## 🙏 Acknowledgments

- **Thanks to all contributors and users** for support and feedback
- **Special thanks to the Anki development team** for the excellent platform
- Thanks to community members for valuable suggestions and bug reports

## 🔒 Privacy Statement

- This add-on will send your card content to the AI service you configured
- Please ensure you understand the privacy policy of the selected AI service provider
- API keys are only stored in local configuration files and will not be uploaded to any server

---

<p align="center">
  <sub>Last Updated: January 2026 | Make learning smarter, make memory more efficient</sub>
</p>
