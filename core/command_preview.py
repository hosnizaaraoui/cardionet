from textual.widgets import Static
from textual.reactive import reactive


class CommandPreview(Static):
    """Command preview widget."""
    cmd: reactive[str] = reactive("$ nmap ")

    def watch_cmd(self, value: str) -> None:
        self.update(f"[b]$ {value}[/]")
