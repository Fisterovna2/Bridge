# AI-Bridge (MVP)

AI-Bridge — это split-brain оркестратор, который позволяет ИИ-агенту **видеть** экран, **действовать** мышью/клавиатурой и при этом соблюдать строгую приватность и безопасность в Normal Mode. Game/Sandbox работают внутри VM через подключаемый адаптер.

## Быстрый старт
```bash
pip install -r requirements.txt
python -m ai_bridge --selfcheck
python -m ai_bridge
```

## Что готово в MVP
- **Privacy Firewall**: захват → OCR → PII → редактирование изображения до отправки в модель.
- **Guardrails**: разрушительные действия блокируются или требуют подтверждения (risk scoring).
- **Kill switch**: любое физическое движение мыши/клавиатуры отменяет очередь действий в Normal Mode.
- **Ghost cursor**: прозрачный оверлей, показывающий намерения агента.
- **Dev Mode**: логи, dry-run, экспорт JSONL сессии.
- **VM Adapter**: заглушка + инструкция для дальнейшей интеграции.

## Структура репозитория
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

## Требования
- Python 3.11+
- Windows 10/11 (Linux поддерживается)
- Установленный Tesseract OCR (используется `pytesseract`)

## Установка

### Windows
1. Установите Python 3.11+.
2. Установите Tesseract OCR:
   - https://github.com/UB-Mannheim/tesseract/wiki
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Запуск UI (основной entrypoint):
   ```bash
   python -m ai_bridge
   ```

### Linux (опционально)
1. Установите Tesseract OCR (пример для Ubuntu):
   ```bash
   sudo apt-get install tesseract-ocr
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запуск UI:
   ```bash
   python -m ai_bridge
   ```

## Preflight checks
- Если **PySide6** отсутствует, `python -m ai_bridge` выводит понятную ошибку.
- Если **Tesseract** отсутствует, UI покажет предупреждение и OCR/редактирование не запустится.

## Использование (MVP)
1. Откройте вкладку **Modes**.
2. Нажмите **Capture + Redact**, чтобы получить отредактированный превью-кадр.
3. Нажмите **Dry-run Demo Action** для демонстрации ghost cursor.
4. Логи доступны во вкладке **Logs / Dev** и сохраняются в `logs/session/session.jsonl`.

## Privacy Firewall (Normal Mode)
1. `capture_screen()`
2. `detect_text_boxes()` (OCR)
3. `detect_pii_entities()` (regex)
4. `redact_image()`
5. **Только отредактированные кадры** используются моделью

## Guardrails (Normal Mode)
- Опасные действия блокируются.
- Medium/high риск требует подтверждения.
- Действия с файлами ограничены allowlist папками.
- Dry-run включен по умолчанию.

## Kill switch (Normal Mode)
Любое движение мыши/клавиатуры отменяет очередь действий. Статус отображается как "Cancelled by user input" до сброса.

## Примеры настройки политики
Политики применяются по режимам, а rule id логируется для каждого решения.
```
models:
  default:
    vision: mvp
    reasoner: mvp
    executor: mvp
  game:
    vision: mvp
    reasoner: mvp
    executor: mvp
  sandbox:
    vision: mvp
    reasoner: backup
    executor: backup
providers:
  mvp:
    type: simple
    fallback: ["backup"]
  backup:
    type: simple
```

## VM интеграция (VirtualBox)
В MVP есть реальный VirtualBox адаптер, который использует `VBoxManage` для запуска/остановки VM,
отката снапшотов, захвата кадров и отправки ввода. Контроль ограничен гостевой VM.

### Настройка VM
1. Установите **VirtualBox** и убедитесь, что `VBoxManage` в PATH.
2. Создайте VM с именем `AI-Bridge` (или измените `config/default.yaml`).
3. Сеть VM: **NAT** или **Host-only** (не мост в локалку).
4. Создайте чистый снапшот `clean`.
5. Установите **VirtualBox Extension Pack**, если нужен VRDE/RDP.
6. (Опционально) Включите **VRDE** (RDP) для отладки:  
   `VBoxManage controlvm <VM_NAME> vrde on`

### Демонстрация
1. Запустите UI: `python -m ai_bridge`
2. Во вкладке **VM** нажмите **Run VM demo**:
   - Запуск VM
   - Захват кадра
   - Движение ghost cursor (dry-run)
   - Ввод текста `hello from AI Bridge` внутри VM

### Game loop (VM-only)
1. Выберите профиль во вкладке **Modes**.
2. Нажмите **Start Game Loop (VM)** для запуска цикла capture→plan→input.
3. Нажмите **Stop Game Loop** для остановки.

### Калибровка
```bash
python -m ai_bridge.tools.calibrate --frame-width 1280 --frame-height 720 --vm-width 1280 --vm-height 720
```

## Тесты
```bash
pytest -q
```

## Observability & Replay
- Логи сессий: `logs/session/session.jsonl` (структурированные, без raw OCR/PII).
- Записи сессий: `logs/session/frames/*.png` и `logs/session/actions.jsonl`.
- Replay (dry-run, только ghost cursor):
  ```bash
  python -m ai_bridge.tools.replay logs/session
  ```

### Audit report
```bash
python -m ai_bridge.tools.audit_report logs/session
```

## Troubleshooting
- **PySide6 / GUI ошибки**: установите PySide6 и используйте среду с GUI.
- **Headless CI**: GUI/host input загружаются лениво, чтобы избежать падений импорта.
- **DISPLAY/libEGL**: запускайте GUI на машине с дисплеем или используйте WSLg.

## Дорожная карта
1. **VM Adapter (реальный)**
   - Looking Glass / IVSHMEM
   - Поток кадров + надежный ввод
2. **Усиленный PII**
   - Presidio/PaddleOCR
   - Политики кастомных сущностей
3. **Policy Engine**
   - Гибкий allowlist/denylist
   - Диалоги подтверждения действий
4. **Model Router**
   - Разделение по ролям
   - Разные провайдеры
5. **Observability**
   - Повтор сессий
   - Метрики и алерты
6. **Security Hardening**
   - Защита от подмены
   - Усиленная изоляция

## Безопасность
- Нет обхода античитов и вредоносных действий.
- Normal Mode **не отправляет** неотредактированные кадры.
