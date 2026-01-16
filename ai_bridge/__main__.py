from __future__ import annotations

import sys

from ai_bridge.preflight import check_gui_dependency


def main() -> int:
    gui_check = check_gui_dependency()
    if not gui_check.is_ok:
        for message in gui_check.messages:
            print(message)
        return 1
    from ai_bridge.ui.app import main as app_main

    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
