from textual.containers import Horizontal, Grid
from textual.widgets import Static, Input, Select, Button
from textual.suggester import SuggestFromList
from textual.containers import Vertical


class ScanConfiguration(Vertical):
    ip_suggestions = ["192.168.0.0/24", "172.16.0.0/16", "10.0.0.0"]
    #Define parameters
    target = Input(placeholder="192.168.1.0/24",
                   suggester=SuggestFromList(ip_suggestions),
                   id="target")
    scan_type = Select(options=[("SYN (-sS)", "sS"), ("TCP (-sT)", "sT"),
                                ("UDP (-sU)", "sU"), ("Host D. (-sn)", "sn"),
                                ("FIN (-sF)", "sF"), ("Ack (-sA)", "sA"),
                                ("Xmas (-sX)", "sX")],
                       value="sS")
    timing = Select(options=[("T0", "T0"), ("T1", "T1"), ("T2", "T2"),
                             ("T3", "T3"), ("T4", "T4"), ("T5", "T5")],
                    value="T4")

    output = Select(options=[("No output", ""), ("Grepables", "oG"),
                             ("XML", "oX")],
                    value="")
    ports = Input(placeholder="22,80,443")

    def compose(self):
        self.classes = "options"
        yield Static("[b]Scan Configuration[/b]\n", expand=False)

        # Target row
        with Horizontal():
            yield Static("[b]Target:[/]", classes="label")
            yield self.target

        # Scan type row
        with Horizontal():
            yield Static("[b]Scan Type:[/]", classes="label")
            yield self.scan_type

        # Timing row
        with Horizontal():
            yield Static("[b]Timing:[/]", classes="label")
            yield self.timing

        # Ports row
        with Horizontal():
            yield Static("[b]Ports:[/]", classes="label")
            yield self.ports

        # Output row
        with Horizontal():
            yield Static("[b]Output:[/]", classes="label")
            yield self.output

        # Extras row
        with Horizontal():
            yield Static("[b]Extras:[/]", classes="label")
            yield Button("Extra Options", id="extras")

        # Scripts row
        with Horizontal():
            yield Static("[b]Scripts:[/]", classes="label")
            yield Button("Open Scripts", id="scripts")

        # Buttons (visual only)
        with Grid(classes="scan_btns"):
            yield Button("Run", id="run")
            yield Button("Clear", id="clear")
            yield Button("Export", id="export")
            yield Button("Manual", id="man")
