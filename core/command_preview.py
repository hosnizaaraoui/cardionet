from textual.widgets import Input
from textual.reactive import reactive


class CommandPreview(Input):
    """Command preview widget."""
    cmd: reactive[str] = reactive("")

    def __init__(self,
                 value=None,
                 placeholder="",
                 highlighter=None,
                 password=False,
                 *,
                 restrict=None,
                 type="text",
                 max_length=0,
                 suggester=None,
                 validators=None,
                 validate_on=None,
                 valid_empty=False,
                 select_on_focus=False,
                 name=None,
                 id=None,
                 classes=None,
                 disabled=False,
                 tooltip=None,
                 compact=False):
        super().__init__(value,
                         placeholder,
                         highlighter,
                         password,
                         restrict=restrict,
                         type=type,
                         max_length=max_length,
                         suggester=suggester,
                         validators=validators,
                         validate_on=validate_on,
                         valid_empty=valid_empty,
                         select_on_focus=select_on_focus,
                         name=name,
                         id=id,
                         classes=classes,
                         disabled=disabled,
                         tooltip=tooltip,
                         compact=compact)

    def watch_cmd(self, value: str) -> None:
        self.value = f"cardionet> {value}"
