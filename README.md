# Curios Agent v2.0

AI-powered desktop automation with computer vision.

## Features

- **Multi-mode operation**: Safe, Fair Play, or Sandbox modes
- **Multiple AI providers**: Gemini, GPT-4V, Claude, Ollama, OpenRouter
- **Plugin system**: Load custom plugins with hot reload
- **Multi-monitor support**: Select and control specific monitors
- **OCR text detection**: Find and click text on screen
- **Custom macros**: Record, save, and playback action sequences
- **Cloud sync**: Backup configurations via GitHub Gist
- **Security**: Built-in protection against harmful actions
- **Privacy**: Auto-blur sensitive data in screenshots
- **Localization**: English and Russian support

## Quick Start

### Installation

```bash
git clone https://github.com/Fisterovna2/Bridge.git
cd Bridge
pip install -r requirements.txt
```

### Get API Keys

You'll need at least one AI provider API key:

- **Gemini**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey) (free tier available)
- **OpenAI**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Claude**: Get from [Anthropic Console](https://console.anthropic.com/)
- **OpenRouter**: Get from [OpenRouter](https://openrouter.ai/keys)
- **Ollama**: Install locally from [Ollama](https://ollama.ai/) (no API key needed)

### Run

```bash
python curios_agent.py
```

## Configuration

On first run, go to **Settings** tab and configure:

1. **Operation Mode**: Choose NORMAL (safe), FAIR_PLAY (VM only), or CURIOS (VM only)
2. **AI Provider**: Select your preferred AI service
3. **API Keys**: Enter API keys for your chosen providers
4. **Monitor**: Select which monitor to control
5. **Language**: Choose English or Russian
6. Click **Save Settings**

## Usage

### Basic Automation

1. Enter your instruction in natural language:
   - "Open notepad and type 'Hello World'"
   - "Find the submit button and click it"
   - "Scroll down and screenshot the page"

2. Click **Execute**
3. In NORMAL mode, confirm each action
4. Watch the **Logs** tab for execution details

### Using OCR

The agent can find and click text on screen:

```
find_text("Login")
click_text("Submit")
```

These commands work automatically when the AI detects text-based tasks.

### Recording Macros

Macros let you record and replay action sequences:

1. Start recording a macro
2. Perform actions manually or via AI
3. Stop recording
4. Save the macro with a name
5. Later, load and execute the saved macro

Macros are stored in `macros/` as JSON files.

### Using Plugins

Plugins extend the agent's capabilities:

1. Place plugin files in `plugins/` directory
2. Plugins are loaded automatically on startup
3. Example plugin available in `plugins/examples/example_plugin.py`

Create custom plugins by extending the `BasePlugin` class:

```python
from plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def on_load(self):
        # Plugin initialization
        return True
    
    def on_action(self, action, context):
        # Called for each action
        return None
    
    def on_unload(self):
        # Plugin cleanup
        return True
```

### Cloud Sync

Sync your settings across devices using GitHub Gist:

1. Create a GitHub personal access token with `gist` scope
2. Add token in Settings under API Keys (github field)
3. Use Cloud Sync features to backup/restore

## Operation Modes

### NORMAL Mode
- Safest option, works anywhere
- Requires confirmation for each action
- Blocks system commands
- Best for learning and testing

### FAIR_PLAY Mode
- **Requires VM environment**
- Human-like timing and input
- For game automation
- Still blocks harmful/financial operations

### CURIOS Mode
- **Requires VM environment**
- Minimal restrictions (sandbox)
- Maximum automation freedom
- Still blocks harmful/financial operations

## Multi-Monitor Support

The agent can detect and control multiple monitors:

- Monitors are auto-detected on startup
- Select target monitor in Settings
- Screenshot specific monitor or all monitors
- Actions are executed on selected monitor

## AI Providers

### Gemini (Google)
- Fast and accurate
- Good for general automation
- Free tier available
- Model: gemini-1.5-flash

### OpenAI GPT-4V
- High quality vision understanding
- Detailed action planning
- Requires paid API access
- Model: gpt-4-vision-preview

### Claude (Anthropic)
- Excellent at complex tasks
- Strong safety alignment
- Requires paid API access
- Model: claude-3-opus-20240229

### Ollama (Local)
- Runs entirely on your machine
- No API key or internet needed
- Requires Ollama installation
- Default model: llava

### OpenRouter
- Access to multiple models
- Pay-per-use pricing
- Flexible model selection
- Good for testing different models

## Security Features

The built-in security system protects against:

- **Harmful actions**: System deletion, process termination, malware
- **Financial operations**: Banking, payments, cryptocurrency
- **System commands**: Shell access, admin operations (in NORMAL mode)
- **Self-protection**: Cannot modify own files
- **VM detection**: Enforces VM requirement for dangerous modes

All logs are auto-sanitized to hide sensitive data like API keys, passwords, and personal information.

## File Structure

```
Bridge/
├── curios_agent.py          # Main application
├── requirements.txt         # Dependencies
├── README.md                # This file
├── README_RU.md             # Russian documentation
├── EULA.md                  # License
├── LEGAL_NOTICE.md          # Legal information
├── .gitignore               # Git ignore rules
├── core/                    # Core modules
│   ├── security.py          # Security kernel
│   ├── driver.py            # Automation driver
│   ├── monitors.py          # Multi-monitor support
│   ├── ocr.py               # OCR engine
│   └── cloud_sync.py        # Cloud synchronization
├── plugins/                 # Plugin system
│   ├── base_plugin.py       # Base plugin class
│   ├── plugin_manager.py    # Plugin manager
│   └── examples/            # Example plugins
├── macros/                  # Macro system
│   └── macro_manager.py     # Macro manager
├── ai_providers/            # AI provider adapters
│   ├── base_provider.py     # Base provider class
│   ├── gemini_provider.py   # Google Gemini
│   ├── openai_provider.py   # OpenAI GPT-4V
│   ├── claude_provider.py   # Anthropic Claude
│   ├── ollama_provider.py   # Ollama (local)
│   └── openrouter_provider.py  # OpenRouter
└── locales/                 # Translations
    ├── en.json              # English
    └── ru.json              # Russian
```

## Troubleshooting

### "AI provider not available"
- Check your API key in Settings
- For Ollama, ensure the service is running: `ollama serve`
- Check your internet connection (except Ollama)

### "This mode requires VM environment"
- FAIR_PLAY and CURIOS modes only work in virtual machines
- Use NORMAL mode on your host machine
- Install VMware, VirtualBox, or similar VM software

### "Action blocked by security system"
- The action was flagged as potentially harmful
- Review what you're trying to do
- This is a safety feature, not a bug

### Mouse/keyboard not working
- Grant screen recording permissions (macOS)
- Enable accessibility permissions
- Check antivirus isn't blocking the app
- Try running as administrator (Windows)

### OCR not detecting text
- Ensure EasyOCR is installed: `pip install easyocr`
- First run downloads language models (may take time)
- Text must be clear and readable
- Try different monitor or screenshot area

## Advanced Usage

### Creating Custom Plugins

See `plugins/examples/example_plugin.py` for a template.

Plugins can:
- Hook into all actions
- Modify behavior
- Add new capabilities
- Persist state between actions

### Writing Macros

Macros are JSON files with this structure:

```json
{
  "name": "my_macro",
  "description": "Does something useful",
  "created_at": "2026-01-05T12:00:00",
  "actions": [
    "move_mouse(100, 200)",
    "click(button='left')",
    "type_text('Hello')"
  ],
  "version": "2.0"
}
```

### Custom AI Prompts

The system prompt can be customized by editing the AI provider files in `ai_providers/`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See [EULA.md](EULA.md) for license terms.

## Legal

See [LEGAL_NOTICE.md](LEGAL_NOTICE.md) for legal information.

## Support

- **Issues**: [GitHub Issues](https://github.com/Fisterovna2/Bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Fisterovna2/Bridge/discussions)

## Roadmap

- [x] Plugin system
- [x] Multi-monitor support
- [x] OCR text detection
- [x] Custom action macros
- [x] Cloud sync
- [x] Multi-AI provider support
- [ ] Mobile companion app (Coming soon - separate repository)
- [ ] Web dashboard
- [ ] Scheduled automation
- [ ] Action templates library

## System Requirements

### Minimum
- Python 3.8+
- 4 GB RAM
- 500 MB disk space
- Internet connection (except Ollama)

### Recommended
- Python 3.10+
- 8 GB RAM
- 2 GB disk space
- Broadband internet

## Credits

- **AI Providers**: Google, OpenAI, Anthropic, Ollama, OpenRouter
- **GUI**: CustomTkinter
- **Automation**: PyAutoGUI, PyDirectInput
- **OCR**: EasyOCR
- **Multi-Monitor**: screeninfo
- **Image Processing**: Pillow

## Changelog

### v2.0 (2026-01-05)
- Added plugin system with hot reload
- Added multi-monitor support
- Added OCR text detection
- Added macro recording and playback
- Added cloud synchronization
- Added multi-AI provider support (OpenAI, Claude, Ollama, OpenRouter)
- Modularized codebase (core/, plugins/, macros/, ai_providers/)
- Improved localization system
- Enhanced security features
- Updated documentation

### v1.0 (2026-01-05)
- Initial release
- Basic automation with Gemini
- Three operation modes
- Security kernel
- Privacy protection
- English/Russian support

---

Made with care for safety and usability.
