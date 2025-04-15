# LexiSage Development Guide

[中文](DEVELOPMENT.md) | English

This document provides detailed information on how to develop, build, and contribute to the LexiSage project.

## Environment Setup
1. Clone this repository
2. Ensure you have Python 3.8+ installed
3. Install dependencies: `pip install -r requirements.txt` (if available)

## Project Structure
- `__init__.py`: Plugin entry point and main functionality
- `config_ui.py`: Configuration UI interface
- `ai_service.py`: AI service API interface
- `prompts.py`: Default prompt templates

## Packaging the Plugin
1. Ensure the project includes the following necessary files:
   - `__init__.py`: Plugin entry point
   - `ai_service.py`: AI service interface
   - `config_ui.py`: Configuration interface
   - `prompts.py`: Default prompts
   - `manifest.json`: Plugin metadata, including name, version, etc.
   - `meta.json`: Anki version compatibility information (important, determines supported Anki versions)
   - `config.json`: Default configuration (optional)
   - `LICENSE`: License file

2. Update version numbers:
   - Update the `version` field in the `manifest.json` file
   - Synchronize the version number in the `ankiweb.json` file (used for AnkiWeb submissions)

3. Package with the following command:
   ```bash
   zip -r anki_lexisage.ankiaddon __init__.py ai_service.py config_ui.py prompts.py manifest.json meta.json LICENSE config.json -x ".*" "__pycache__/*" "*.pyc"
   ```

4. Verify package contents:
   ```bash
   unzip -l anki_lexisage.ankiaddon
   ```
   Ensure it contains only necessary files, without extraneous `.git`, `__pycache__`, etc.

5. Test installation:
   - Install the `.ankiaddon` file in a test environment using Anki's "Install from file" function
   - Verify that the plugin functions correctly

## Submitting to AnkiWeb
1. Register an [AnkiWeb account](https://ankiweb.net/account/register)
2. After logging in, visit the [sharing page](https://ankiweb.net/shared/info/)
3. Click "Upload Add-on" to submit your plugin
4. Fill in plugin information and upload the packaged file
5. Wait for approval

## Contribution Guidelines
Contributions of code, issue reports, or feature suggestions are welcome!

1. Fork this repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request
