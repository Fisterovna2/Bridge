# AI-Bridge (MVP)

AI-Bridge — это split-brain оркестратор, который позволяет ИИ-агенту **видеть** экран, **действовать** мышью/клавиатурой и при этом соблюдать строгую приватность и безопасность в Normal Mode. Game/Sandbox работают внутри VM через подключаемый адаптер.

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
4. Логи доступны во вкладке **Logs / Dev** и сохраняются в `logs/session.jsonl`.

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

## VM интеграция (MVP)
Адаптер-заглушка реализует:
- `start_vm()`
- `stop_vm()`
- `snapshot_revert()`
- `get_frame()`
- `send_input()`

### Следующий шаг: VirtualBox адаптер
1. Включите **VRDE** (RDP) на VM.
2. Используйте `VBoxManage controlvm <VM_NAME> vrde on`.
3. Захват кадров через RDP или shared folder screenshot hook.
4. Реализуйте `snapshot_revert` через `VBoxManage snapshot <VM_NAME> restore <SNAPSHOT>`.

## Тесты
```bash
pytest -q
```

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
