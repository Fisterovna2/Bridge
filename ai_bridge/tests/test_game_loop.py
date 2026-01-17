import time
from PIL import Image

from ai_bridge.core.cancellation import CancellationToken
from ai_bridge.game.loop import GameLoop
from ai_bridge.vm.adapter_base import VmAdapter
from ai_bridge.core.actions import Action


class DummyAdapter(VmAdapter):
    def __init__(self) -> None:
        self.sent = 0

    def start_vm(self) -> None:
        return None

    def stop_vm(self) -> None:
        return None

    def snapshot_revert(self, snapshot_name: str | None = None) -> None:
        return None

    def get_frame(self):
        return Image.new("RGB", (10, 10))

    def send_input(self, action: Action) -> None:
        self.sent += 1

    def status(self) -> str:
        return "ok"


def test_game_loop_vm_only_and_cancellation() -> None:
    token = CancellationToken.create()
    adapter = DummyAdapter()
    loop = GameLoop(
        adapter=adapter,
        ghost_cursor=lambda action: None,
        cancellation=token,
        dry_run=False,
    )
    loop.start()
    time.sleep(0.2)
    token.cancel()
    loop.stop()
    assert adapter.sent >= 0
