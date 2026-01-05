# Curios Agent v1.0

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-See%20EULA-orange)
![Status](https://img.shields.io/badge/status-stable-green)

**AI-powered desktop automation agent with computer vision capabilities.**

Curios Agent is an intelligent desktop automation tool that combines AI vision (Google Gemini) with computer control to execute complex tasks on your PC. Built with safety and privacy in mind.

## ✨ Features

### 🎮 Multi-Mode Operation
- **NORMAL** - Safe mode with user confirmations (works everywhere)
- **FAIR_PLAY** - Human-like behavior for games (VM only)
- **CURIOS** - Sandbox mode without restrictions (VM only)

### 🛡️ Built-in Security Kernel
- ✅ Blocks malicious actions (system damage, malware, etc.)
- ✅ Blocks financial operations (payments, transactions)
- ✅ Blocks system commands in NORMAL mode
- ✅ Self-protection: cannot modify own files
- ✅ VM detection for dangerous modes
- ✅ Comprehensive logging of all actions

### 🔒 Privacy Protection
- Blurs sensitive data on screenshots before sending to AI
- Sanitizes logs (auto-hides API keys, passwords, tokens, emails, phone numbers)
- No data collection or telemetry

### 🤖 AI-Powered Automation
- Computer vision with Google Gemini 1.5 Flash
- Natural language instructions
- Automatic action planning and execution
- Mouse and keyboard control
- Screenshot analysis

### 🌍 Multi-Language Support
- English (EN)
- Russian (RU)

### 🖥️ User-Friendly GUI
- Modern CustomTkinter interface
- Tabbed layout (Control Panel, Settings, Logs, About)
- Real-time status updates
- Dark theme

## 📋 Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, Linux, macOS
- **VM**: Required for FAIR_PLAY and CURIOS modes
- **API Key**: Google Gemini API key (free tier available)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Fisterovna2/Bridge.git
cd Bridge
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 4. Run the application
```bash
python curios_agent.py
```

### 5. Configure
1. Open **Settings** tab
2. Paste your Gemini API key
3. Select operation mode
4. Choose language
5. Click **Save Settings**

## 📖 Usage

### Basic Workflow

1. **Enter Instruction**: In the Control Panel tab, type your task in natural language
   - Example: "Open notepad and type 'Hello World'"
   - Example: "Find and click the submit button"
   - Example: "Scroll down and take a screenshot"

2. **Execute**: Click the "Execute" button
   - The agent will analyze your screen
   - AI will plan the necessary actions
   - Actions will be executed (with confirmations in NORMAL mode)

3. **Monitor**: Watch the Logs tab for real-time execution details

### Operation Modes

#### NORMAL Mode (Recommended)
- **Use Case**: General automation, learning, safe experimentation
- **Safety**: Requires user confirmation for each action
- **Restrictions**: Blocks system commands, harmful actions, financial operations
- **Works**: Anywhere (host OS, VM)

#### FAIR_PLAY Mode
- **Use Case**: Game automation with human-like behavior
- **Safety**: Uses human-like timing and input methods
- **Restrictions**: Blocks harmful actions, financial operations
- **Works**: VM only (will refuse to run on host OS)

#### CURIOS Mode
- **Use Case**: Advanced automation, testing in sandbox
- **Safety**: Minimal restrictions (still blocks harmful/financial actions)
- **Restrictions**: Blocks harmful actions, financial operations
- **Works**: VM only (will refuse to run on host OS)

### Example Instructions

**Web Browsing:**
```
Open Chrome and navigate to wikipedia.org
```

**File Operations:**
```
Create a new text file and save it as 'report.txt'
```

**Data Entry:**
```
Fill in the form with: Name: John, Email: john@example.com
```

**Research:**
```
Search for 'Python automation' and open the first 3 results
```

## 🛡️ Security Features

### SecurityKernel Protection

The SecurityKernel monitors all actions and blocks:

1. **Harmful Actions**
   - System deletion (delete system32, rm -rf /, format c:)
   - Process termination (shutdown, kill, taskkill)
   - Malware keywords (virus, ransomware, exploit, hack)
   - Data destruction (dd, wipe, corrupt)

2. **Financial Operations**
   - Banking operations
   - Payment processing
   - Cryptocurrency transactions
   - Money transfers

3. **System Commands** (in NORMAL mode)
   - Command line execution (cmd, powershell, bash)
   - Administrative actions (sudo, run as admin)
   - System installers

4. **Private Data Protection**
   - Cannot access passwords, credentials, tokens
   - Cannot read API keys, SSH keys
   - Screenshots blur sensitive areas
   - Logs auto-sanitize sensitive data

5. **Self-Protection**
   - Cannot modify `curios_agent.py`
   - Cannot modify `curios_config.json`
   - Cannot modify `agent_system.log`

### Privacy Features

**Screenshot Privacy:**
- Automatically blurs sensitive areas before sending to AI
- Configurable in settings

**Log Sanitization:**
- API keys: `api_key: ***`
- Passwords: `password: ***`
- Tokens: `token: ***`
- Emails: `***@***.***`
- Phone numbers: `***-***-****`

### VM Detection

For FAIR_PLAY and CURIOS modes, the agent:
- Detects VM environment (VMware, VirtualBox, QEMU, Hyper-V, etc.)
- Refuses to run dangerous modes on host OS
- Provides clear error messages

## 📁 File Structure

```
Bridge/
├── curios_agent.py        # Main application (DO NOT EDIT)
├── requirements.txt       # Python dependencies
├── curios_config.json     # Configuration (auto-generated)
├── agent_system.log       # Activity logs (auto-generated)
├── README.md             # This file
├── EULA.md               # License agreement
├── LEGAL_NOTICE.md       # Legal warnings
└── .gitignore            # Git ignore rules
```

## ⚙️ Configuration

Configuration is stored in `curios_config.json`:

```json
{
  "mode": "NORMAL",
  "language": "en",
  "api_key": "your_gemini_api_key",
  "mouse_speed": 0.5,
  "typing_speed": 0.1,
  "screenshot_privacy": true,
  "log_sanitization": true
}
```

### Configuration Options

- `mode`: Operation mode (NORMAL/FAIR_PLAY/CURIOS)
- `language`: UI language (en/ru)
- `api_key`: Google Gemini API key
- `mouse_speed`: Mouse movement duration (0.1-2.0 seconds)
- `typing_speed`: Typing interval (0.01-0.5 seconds)
- `screenshot_privacy`: Enable privacy blur (true/false)
- `log_sanitization`: Enable log sanitization (true/false)

## 🔧 Troubleshooting

### "Gemini API not initialized"
**Solution**: Add your API key in Settings tab

### "This mode requires VM environment"
**Solution**: Use NORMAL mode on host OS, or run in VM for other modes

### "Action blocked by SecurityKernel"
**Solution**: The action is blocked for safety. Review security features.

### Mouse/Keyboard not working
**Solution**: 
- Check permissions (screen recording, accessibility)
- Disable pyautogui FAILSAFE (move mouse to corner)
- Try restarting application

### AI produces wrong actions
**Solution**:
- Provide more detailed instructions
- Use step-by-step approach
- Check screenshot quality

## 🤝 Contributing

Contributions are welcome! Please read [EULA.md](EULA.md) and [LEGAL_NOTICE.md](LEGAL_NOTICE.md) first.

### Guidelines
- Maintain security features
- Add tests for new features
- Follow code style
- Update documentation

## 📜 License

See [EULA.md](EULA.md) for license terms.

## ⚖️ Legal

See [LEGAL_NOTICE.md](LEGAL_NOTICE.md) for legal information and warnings.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. The authors and contributors are not responsible for any damage, data loss, or legal consequences resulting from the use of this software.

**Use at your own risk. Always test in a safe environment first.**

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Fisterovna2/Bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Fisterovna2/Bridge/discussions)

## 🎯 Roadmap

- [ ] Plugin system
- [ ] Multi-monitor support
- [ ] OCR text detection
- [ ] Custom action macros
- [ ] Cloud sync for configurations
- [ ] Mobile companion app

## 📊 System Requirements

### Minimum
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Disk: 500 MB free space
- Internet: Required for AI features

### Recommended
- CPU: Quad-core 2.5 GHz+
- RAM: 8 GB+
- Disk: 1 GB free space
- Internet: Broadband connection

## 🏆 Credits

- **AI**: Google Gemini 1.5 Flash
- **GUI**: CustomTkinter
- **Automation**: PyAutoGUI, PyDirectInput
- **Image**: Pillow

## 📝 Changelog

### v1.0 (2026-01-05)
- Initial release
- Multi-mode operation (NORMAL/FAIR_PLAY/CURIOS)
- SecurityKernel with comprehensive protection
- Privacy features (blur, sanitization)
- AI-powered automation (Gemini 1.5 Flash)
- Multi-language support (EN/RU)
- CustomTkinter GUI
- Complete documentation

---

**Built with ❤️ and 🔒 by the Bridge Team**