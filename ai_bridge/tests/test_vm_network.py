from ai_bridge.vm.adapter_virtualbox import VirtualBoxAdapter


def test_network_mode_enforcement() -> None:
    adapter = VirtualBoxAdapter(vm_name="TestVM", vboxmanage_path="VBoxManage")

    def fake_output(*args: str) -> str:
        return 'nic1="bridged"'

    adapter._run_output = fake_output  # type: ignore[assignment]
    ok, mode = adapter._network_mode()
    assert ok is False
    assert mode == "bridged"
