# LexiSage - AI Definition Generator for Anki

English | [中文](README.md)

> LexiSage – Let your cards speak with clarity and wisdom.

## Project Overview
[LexiSage](https://ankiweb.net/shared/info/750479332?cb=1744698675805) is an intelligent definition plugin designed for Anki that supports multiple AI interfaces (OpenAI, XAI, DeepSeek) to generate explanations for selected fields. It's especially useful for language learners.

### Key Features
- Automatic parsing of word meanings and usage
- Context-based word explanations
- Batch processing to improve study efficiency
- Customizable system prompts
- Support for multiple note types
- Support for various AI services (requires your own API Keys)

## Installation

1. In Anki, click "Tools" > "Add-ons"
2. Click "Get Add-ons"
3. Enter the add-on code: **750479332**
4. Restart Anki

## Usage Instructions

### Basic Configuration

1. Open Anki, select "LexiSage Settings..." from the "Tools" menu
2. Set up AI services. The plugin doesn't provide AI services itself, so you need to purchase API Keys from AI service providers and enter them into the plugin. After obtaining an API Key, select the corresponding service provider and fill in the correct API Key and the model you want to use.
   Recommended AI service providers:
   - [xAI](https://console.x.ai) (Great value: $5 monthly charge gives you $150 credit)
   - [DeepSeek](https://platform.deepseek.com) (Leading Chinese AI platform)

   ![image](https://github.com/user-attachments/assets/1d33d54d-ca04-4507-83bd-84267557fb0a)
3. Add configuration for your note types, specify which template fields the AI should explain, designate output result fields, and optionally add context for more accurate definitions.

   ![image](https://github.com/user-attachments/assets/ca6f59d6-ab80-4911-b6e0-24c5f3fa0e49)

   - Click the + button to add note type configuration
   - Select the field to explain
   - Select context field (optional)
   - Select destination field for definitions
   - Save configuration
   (This plugin supports configuring multiple note types, allowing batch processing of different note types simultaneously)

### Generating Definitions

1. Browse your card collection
2. Select the cards for which you want to generate definitions
3. Click "LexiSage" > "Generate Batch Definitions" in the menu bar, then wait for completion

   ![image](https://github.com/user-attachments/assets/6ebbb32e-e9a9-4f84-96d1-cc05041e3b8c)

### Custom Prompts

The plugin includes built-in prompts, but if you're not satisfied with the definition results, you can customize the prompts in "LexiSage Settings"

## Developer Guide

If you want to understand the project structure, build process, or want to contribute, please check our [Development Guide](DEVELOPMENT_EN.md).

## License
This project uses the [MIT License](LICENSE) - see the LICENSE file for details.

## Acknowledgements
- Thanks to all contributors and users
- Special thanks to the Anki development team for providing an excellent platform

## Supported AI Services
- **OpenAI**: Supports GPT-3.5/GPT-4 and other models
- **XAI**: Supports custom API interfaces
- **DeepSeek**: Supports DeepSeek Chat models

## Custom Prompts
In prompt templates, you can use the following variables:
- `{word}`: Represents the content of the field to explain
- `{context}`: Represents the content of the context field (if any)

## Troubleshooting
- If the plugin doesn't work properly, check:
  - Whether your API key is correct
  - Whether your network connection is stable
  - Whether you've selected the correct fields
- If you encounter problems, try restarting Anki

## Privacy Statement
This plugin sends your card content to the AI service you configure, so please ensure you understand the relevant privacy policies. API keys are stored only in local configuration files and are not uploaded.
