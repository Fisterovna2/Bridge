# AI-Bridge (MVP)

AI-Bridge is a split-brain orchestrator that lets an AI agent **see** the screen, **act** via mouse/keyboard, and do so with strict privacy and safety controls in Normal Mode. Game/Sandbox modes operate inside a VM boundary using a pluggable VM adapter.

## MVP Highlights
- **Normal Mode privacy firewall**: capture → OCR → PII detection → redact image before any model use.
- **Guardrails**: destructive actions are blocked or require confirmation (risk scoring).
- **Kill switch**: any physical mouse/keyboard input cancels the action queue in Normal Mode.
- **Ghost cursor overlay**: translucent cursor showing intended actions with delay + animation.
- **Dev Mode**: logs, dry-run (simulate input), export session JSONL.
- **VM Adapter interface**: placeholder adapter + instructions for real VM integration.

## Repository Structure
```
ai_bridge/
  core/
    orchestrator.py
    modes.py
    actions.py
    safety.py
    router.py
    model_provider.py
    cancellation.py
  vision/
    capture.py
    ocr.py
    pii.py
    redact.py
  input/
    host_input.py
    vm_input.py
    ghost_cursor.py
    kill_switch.py
  vm/
    adapter_base.py
    adapter_placeholder.py
  ui/
    app.py
    main_window.py
    widgets.py
  config/
    default.yaml
  logs/
  tests/
```

## Requirements
- Python 3.11+
- Windows 10/11 (Linux supported for MVP)
- Tesseract OCR installed (used by `pytesseract`)

## Installation

### Windows
1. Install Python 3.11+.
2. Install Tesseract OCR:
   - https://github.com/UB-Mannheim/tesseract/wiki
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the UI (primary entrypoint):
   ```bash
   python -m ai_bridge
   ```

### Linux (optional)
1. Install Tesseract OCR (example for Ubuntu):
   ```bash
   sudo apt-get install tesseract-ocr
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the UI:
   ```bash
   python -m ai_bridge
   ```

## Preflight checks
- If **PySide6** is missing, `python -m ai_bridge` prints a clear error.
- If **Tesseract** is missing, the UI shows a warning and OCR/redaction will not run.

## Usage (MVP)
1. Open **Modes** tab.
2. Click **Capture + Redact** to generate a redacted preview image.
3. Click **Dry-run Demo Action** to move the ghost cursor to a demo location without clicking.
4. Logs appear in **Logs / Dev** tab, and are saved to `logs/session.jsonl`.

## Privacy Firewall (Normal Mode)
Pipeline enforced by the orchestrator:
1. `capture_screen()`
2. `detect_text_boxes()` (OCR)
3. `detect_pii_entities()` (regex)
4. `redact_image()`
5. **Only redacted frames are used**

## Guardrails (Normal Mode)
- Destructive actions are blocked.
- Medium/high risk actions require confirmation.
- File actions are restricted to allowlisted paths.
- Dry-run is enabled by default.

## Kill switch (Normal Mode)
Any physical mouse/keyboard input cancels the current action queue. The UI shows status "Cancelled by user input" until reset.

## VM Integration (MVP)
The placeholder adapter implements:
- `start_vm()`
- `stop_vm()`
- `snapshot_revert()`
- `get_frame()`
- `send_input()`

### Next step: VirtualBox adapter (suggested)
1. Enable **VRDE** (RDP) on the VM.
2. Use `VBoxManage controlvm <VM_NAME> vrde on`.
3. Capture frames via RDP or a shared folder screenshot hook.
4. Implement `snapshot_revert` with `VBoxManage snapshot <VM_NAME> restore <SNAPSHOT>`.

## Tests
```bash
pytest -q
```

## Roadmap to Full Version
1. **VM Adapter (real)**
   - Looking Glass / IVSHMEM
   - Streamed frames + reliable input injection
2. **Robust PII**
   - Presidio/PaddleOCR integration
   - Custom entity patterns and policies
3. **Policy Engine**
   - Fine-grained allowlist/denylist
   - Per-action confirmations with UI dialogs
4. **Model Router**
   - Multi-model routing by role
   - Vision/Planner/Executor per provider
5. **Observability**
   - Session replay
   - Metrics + alerting
6. **Security Hardening**
   - Tamper detection
   - Stronger sandboxing for Normal Mode

## Safety Notes
- No anti-cheat bypass or exploit behavior is implemented.
- Normal Mode does **not** send unredacted frames to any model.
