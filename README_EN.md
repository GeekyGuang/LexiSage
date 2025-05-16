# LexiSage - AI Definition Generator for Anki

English | [中文](README.md)

> LexiSage – Let your cards speak with clarity and wisdom.

## Project Overview
[LexiSage](https://ankiweb.net/shared/info/750479332?cb=1744698675805) is an intelligent definition plugin designed for Anki that supports multiple AI interfaces (OpenAI, XAI, DeepSeek) to generate explanations for selected fields. It's especially useful for language learners.

### Key Features
- Automatic parsing of word meanings and usage
- Context-based word explanations
- Batch processing to improve study efficiency
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


   ![image](https://github.com/user-attachments/assets/372d2766-49de-48fd-8333-0acd741fa6ab)

3. Add configuration for your note types, specify which template fields the AI should explain, designate output result fields, and optionally add context for more accurate definitions.

   ![image](https://github.com/user-attachments/assets/cb48ee74-3e36-4fc1-9ff9-14af6d3c5179)

   - Click the + button to add note type configuration
   - Select note type
   - Select the field to explain
   - Select context field (optional)
   - Select destination field for definitions
   - Save configuration
   (This plugin supports configuring multiple note types, allowing batch processing of different note types simultaneously)

### Generating Definitions

1. Browse your card collection
2. Select cards for which you want to generate definitions
3. Click "LexiSage" > "Generate Batch Definitions" in the menu bar, then wait for completion

   ![image](https://github.com/user-attachments/assets/6ebbb32e-e9a9-4f84-96d1-cc05041e3b8c)

### Custom Prompts

The plugin includes built-in prompts, but if you're not satisfied with the definition results, you can customize the prompts in "LexiSage Settings"

## Developer Guide

If you want to understand the project structure, build process, or want to contribute, please check our [Development Guide](DEVELOPMENT_EN.md).

## License
This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE) - see the LICENSE file for details.

## Acknowledgements
- Thanks to all contributors and users
- Special thanks to the Anki development team for providing an excellent platform

## Privacy Statement
This plugin sends your card content to the AI service you configure, so please ensure you understand the relevant privacy policies. API keys are stored only in local configuration files and are not uploaded.
