# LexiSage Development Guide

[Chinese](DEVELOPMENT.md) | [English](DEVELOPMENT_EN.md)

This document provides detailed information on how to develop, build, and contribute to the LexiSage project. LexiSage is an Anki add-on that uses AI to generate word definitions, synonyms, grammar notes, and example sentences for language learners.

## Project Architecture Overview

LexiSage adopts a modular design, separating different functionalities into independent Python files for easy maintenance and extension. The entire add-on follows an MVC-like pattern:
- **Model Layer**: `ai_service.py` and `prompts.py` handle data logic and AI interaction
- **View Layer**: `config_ui.py` provides the user interface
- **Controller Layer**: `__init__.py` serves as the entry point coordinating all modules

## Detailed File Structure

### 1. `__init__.py` - Add-on Entry Point
**Core Functionality**: The main entry point of the add-on, responsible for registering Anki hooks and coordinating the work of each module.
**Main Contents**:
- `BatchGenerationWorker`: Background thread class for batch generation of explanations, avoiding UI freezing
- `save_results()`: Writes AI-generated results back to the Anki database, including transaction handling
- `on_browser_batch_generate()`: Browser batch generation functionality
- `on_editor_gen()`: Editor single-card generation functionality
- `setup_browser_menu()`: Adds LexiSage menu to the Anki browser
- `add_editor_button()`: Adds LexiSage button to the editor
**Key Features**:
- Complete exception handling and resource cleanup
- Database transaction rollback mechanism, preventing data corruption
- Progress dialog management, ensuring UI responsiveness

### 2. `ai_service.py` - AI Service Layer
**Core Functionality**: Encapsulates communication logic with various AI services (OpenAI, XAI, DeepSeek).
**Main Contents**:
- `generate_batch_explanation()`: Core function that constructs JSON payload and calls AI services
- `ExplanationTask`: Class representing a single explanation generation task
- `ProgressTracker`: Multi-threading progress tracker
- `generate_explanations_batch()`: Function for batch processing multiple tasks
- `format_text_to_html()`: Tool function for cleaning AI-returned text
**Key Features**:
- Supports multi-threaded concurrent requests
- Complete logging system (lexisage.log)
- Automatic retry mechanism (maximum 2 retries)
- Unified API interface supporting multiple AI services

### 3. `config_ui.py` - Configuration Interface
**Core Functionality**: Provides user-friendly configuration interface for managing add-on settings.
**Main Contents**:
- `ConfigDialog`: Main configuration dialog class containing three tabs
- `NoteTypeConfig`: Data class for note type configuration
- Three tabs:
  1. **Note Type Settings**: Configure field mappings and prompts for different note types
  2. **AI System Instructions**: Set global AI system prompts
  3. **AI Service Settings**: Configure API keys, model parameters, and advanced options
**Key Features**:
- Dynamic UI updates with real-time preview of AI sending content
- Configuration validation and error handling
- Default template viewing functionality

### 4. `prompts.py` - Prompt Management
**Core Functionality**: Centralized management of all AI prompt templates, providing default configurations.
**Main Contents**:
- `DEFAULT_GLOBAL_SYSTEM_PROMPT`: Global system prompt defining AI role and behavior specifications
- `DEFAULT_FIELD_PROMPT_TEMPLATE`: Default field prompt used when a field has no custom prompt configured
- `BATCH_INSTRUCTION_TEMPLATE`: UI preview template for display purposes only
**Key Features**:
- Clear three-layer prompt architecture (system layer, instruction layer, preview layer)
- Unified string format supporting variable substitution (`{word}`, `{context}`)
- Adheres to "Feynman Principle", emphasizing easy-to-understand explanations

## Code Architecture Advantages

1. **Separation of Concerns**: UI logic, business logic, and AI communication logic separated into different files
2. **Extensibility**: Easy to add new AI services or functional modules
3. **Maintainability**: Clear module boundaries and responsibility division
4. **Error Handling**: Comprehensive exception catching and user-friendly error prompts
5. **Configuration Management**: Unified configuration system supporting multiple note types

## Future Refactoring Suggestions

### 1. Further Modularization
**Suggestion**: Further split large files into smaller specialized modules.
- Create `threading_utils.py`: Centralize multi-threading related code (`BatchGenerationWorker`, `ProgressTracker`)
- Create `database_utils.py`: Handle all database operations (`save_results`, field checking functions)
- Create `logging_utils.py`: Unified logging and error handling

### 2. Configuration System Improvements
**Suggestion**: Use more structured configuration management.
- Introduce configuration validation and migration tools
- Support configuration version upgrades
- Add configuration import/export functionality

### 3. Testing Framework
**Suggestion**: Establish a complete test suite.
- Unit tests: Test core functionality of each module
- Integration tests: Test inter-module collaboration
- End-to-end tests: Simulate usage scenarios in real Anki environment

### 4. Internationalization Support
**Suggestion**: Provide support for multilingual users.
- Extract all UI text to translation files
- Support dynamic language switching
- Provide translation contribution guidelines

## Development Environment Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/{your-username}/LexiSage.git
   cd LexiSage
   ```

2. **Python Environment**:
   - Requires Python 3.8 or higher
   - Recommended to use virtual environment: `python -m venv venv`
   - Activate virtual environment:
     - Windows: `venv\Scripts\activate`
     - macOS/Linux: `source venv/bin/activate`

3. **Dependency Installation**:
   ```bash
   pip install requests
   # Install other dependencies as needed
   ```

4. **Anki Development Environment**:
   - Link the add-on directory to Anki's addons21 folder
   - Restart Anki to load the add-on
   - Use Anki's development tools for debugging

## Packaging the Add-on

1. **Ensure necessary files are included**:
   - `__init__.py`: Add-on entry point
   - `ai_service.py`: AI service interface
   - `config_ui.py`: Configuration interface
   - `prompts.py`: Default prompts
   - `manifest.json`: Add-on metadata, including name, version, etc.
   - `meta.json`: Anki version compatibility information (important, determines supported Anki versions)
   - `config.json`: Default configuration (optional)
   - `LICENSE`: License file (GNU General Public License v3.0)

2. **Update version numbers**:
   - Update the `version` field in `manifest.json`
   - Synchronize version number in `ankiweb.json`

3. **Package command**:
   ```bash
   zip -r LexiSage.ankiaddon __init__.py ai_service.py config_ui.py prompts.py manifest.json meta.json LICENSE -x ".*" "__pycache__/*" "*.pyc"
   ```

4. **Verify package contents**:
   ```bash
   unzip -l LexiSage.ankiaddon
   ```
   Ensure it doesn't contain extraneous files like `.git`, `__pycache__`, etc.

## Submitting to AnkiWeb

1. Register an [AnkiWeb account](https://ankiweb.net/account/register)
2. After logging in, visit the [sharing page](https://ankiweb.net/shared/info/)
3. Click "Upload Add-on" to submit your add-on
4. Fill in add-on information and upload the packaged file
5. Wait for approval

## Contribution Guidelines

Welcome contributions of code, issue reports, or feature suggestions!

1. **Fork repository**: Fork this repository on GitHub
2. **Create branch**: `git checkout -b feature/your-feature-name`
3. **Commit changes**: `git commit -m 'Add some feature'`
4. **Push branch**: `git push origin feature/your-feature-name`
5. **Create PR**: Create a Pull Request on GitHub

### Code standards
- Follow PEP 8 code style
- Add appropriate comments and docstrings
- Ensure new features have corresponding error handling
- Update relevant documentation

### Testing requirements
- New features should include test cases
- Ensure existing tests pass
- Update test documentation

## Troubleshooting

### Common issues
1. **AI service connection failure**: Check API keys and network connection
2. **Configuration save failure**: Check file permissions and disk space
3. **UI display abnormalities**: Restart Anki or clear cache

### Debugging tips
1. **View log file**: After running one field filling operation, `lexisage.log` records all API requests and errors
2. **Simplify configuration**: Start with minimal configuration, gradually add complex features

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). For details, see the [LICENSE](LICENSE) file.

---

*Last Updated: January 2026*
*Version: Based on analysis and optimization suggestions of current LexiSage architecture*
