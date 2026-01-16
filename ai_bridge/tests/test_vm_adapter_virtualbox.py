from pathlib import Path

from PIL import Image

from ai_bridge.vm.adapter_virtualbox import VirtualBoxAdapter


def test_virtualbox_state_machine(tmp_path: Path) -> None:
    adapter = VirtualBoxAdapter(vm_name="TestVM", vboxmanage_path="VBoxManage")
    calls = []

    def fake_run(*args: str) -> None:
        calls.append(args)
        if "screenshotpng" in args:
            image = Image.new("RGB", (10, 10), (0, 0, 0))
            image.save(adapter.frame_path)

    adapter.frame_path = tmp_path / "frame.png"
    adapter._run = fake_run  # type: ignore[assignment]

    adapter.start_vm()
    assert adapter.status().startswith("Running")
    adapter.get_frame()
    adapter.snapshot_revert("clean")
    adapter.stop_vm()

    assert any("startvm" in call for call in calls)
    assert any("screenshotpng" in call for call in calls)
    assert any("snapshot" in call for call in calls)
    assert any("poweroff" in call for call in calls)
