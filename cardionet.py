#!/usr/bin/env python3
from datetime import datetime
from core.theme import cardionet_neon
from core.logs import Logs
from core.command_preview import CommandPreview
from core.scan_config import ScanConfiguration
from ui.modals import ExportModal, ExtraModal, QuitModal, ScriptsModal
from textual.app import App, ComposeResult
from textual import on
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Button, Select, Checkbox, Input

APP_VERSION = "0.1"
APP_NAME = open("assets/app_logo.txt").read()
MANUAL = open("assets/manual.txt").read()


class CardioNetApp(App):
    CSS_PATH = "assets/app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "run_scan", "Run"),
        ("c", "clear_logs", "Clear"),
        ("e", "open_export_modal", "Export"),
        ("?", "display_manual", "Manual"),
    ]

    scan = ScanConfiguration()
    os = False
    verbose = False
    version_detection = False
    script = ""
    output_file = ""

    def on_mount(self):
        self.register_theme(cardionet_neon)

        self.theme = "cardionet_neon"

    def compose(self) -> ComposeResult:
        # Header
        header_text = f"{APP_NAME}  |  v{APP_VERSION}"
        yield Static(header_text, classes="header")

        # Command preview
        self.cmd_preview = CommandPreview(classes="cmd")

        # Pre-fill with a representative command for the visual prototype
        self.cmd_preview.cmd = "$ nmap"
        yield self.cmd_preview

        # Main horizontal split: options (left) and results (right)
        with Horizontal(classes="main"):
            # Options panel
            yield self.scan

            # Results panel
            with Vertical(classes="results"):
                yield Static("[b]Live Results[/b] ", expand=False)
                # RichLog is used as a scrolling result area
                self.results_log = Logs(classes="logs")

                yield VerticalScroll(self.results_log)

        # Footer with shortcuts
        footer_text = "[$warning bold]\[R][/] Run   [$warning bold]\[E][/] Export   [$warning bold]\[C][/] Clear   [$warning bold]\[?][/] Manual   [$warning bold]\[Q][/] Quit"
        yield Static(footer_text, classes="footer")

    # Event Handlers
    @on(Button.Pressed, "#run")
    async def action_run_scan(self):
        """Execute nmap scan and display results in log"""
        self.results_log.clear()
        log_widget = self.results_log
        await log_widget.stream_process(self.cmd_preview.cmd.split(" "))

    @on(Button.Pressed, "#man")
    async def action_display_manual(self):
        """Display CardioNet manual"""
        self.results_log.clear()
        self.results_log.write(MANUAL, scroll_end=False)

    @on(Button.Pressed, "#clear")
    def action_clear_logs(self):
        """Clear scan results log"""
        self.results_log.clear()

    @on(Button.Pressed, "#apply")
    @on(Select.Changed)
    @on(Input.Changed)
    def handle_parameters_changed(self):
        """Rebuild nmap command when scan parameters change"""
        command_as_list = ["nmap"]

        # Scan configuration
        command_as_list.append(f"-{self.scan.scan_type.value}")  # Scan type
        command_as_list.append(f"-{self.scan.timing.value}")  # Timing template

        # Port range (default to 1-1000 if empty)
        if self.scan.scan_type.value != "sn":
            command_as_list.append("-p")
            command_as_list.append(self.scan.ports.value or "1-1000")
        else:
            self.scan.ports.disabled = True

        #Output
        if self.scan.output.value != "":
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = self.scan.target.value.replace("/", "_").replace(
                ".", "_")

            # Determine file extension based on output format
            extension_map = {"oG": "gnmap", "oX": "xml"}
            ext = extension_map.get(self.scan.output.value, "txt")

            # Create filename in /tmp
            filename = f"/tmp/nmap_scan_{target_name}_{timestamp}.{ext}"
            self.output_file = filename

            # Always save normal output
            command_as_list.append(
                f"-oN /tmp/nmap_scan_{target_name}_{timestamp}.nmap")

            command_as_list.append(f"-{self.scan.output.value} {filename}")

        # Optional features
        if self.os: command_as_list.append("-O")
        if self.version_detection: command_as_list.append("-sV")
        if self.script and self.script != "Select.BLANK":
            command_as_list.append(f"--script={self.script}")
        if self.verbose: command_as_list.append("-vv")

        # Target
        if self.scan.target.value.strip():
            command_as_list.append(self.scan.target.value)

        # Update command preview
        self.cmd_preview.cmd = " ".join(command_as_list)

    # Modals
    @on(Button.Pressed, "#extras")
    def open_extras_modal(self):
        """Open extra options modal"""
        extras = ExtraModal()
        self.push_screen(extras, self._get_extra_options)

    def _get_extra_options(self, options: list):
        """Update scan options from extras modal"""
        self.verbose, self.os, self.version_detection = options

    @on(Button.Pressed, "#scripts")
    def open_scripts_modal(self):
        """Open nmap scripts modal"""
        scripts = ScriptsModal()
        self.push_screen(scripts, self._get_chosen_script)

    def _get_chosen_script(self, script: str):
        """Handle the result of scripts modal"""
        if script:
            self.script = script

    @on(Button.Pressed, "#export")
    def action_open_export_modal(self):
        """Open nmap export modal"""
        if self.output_file:
            export = ExportModal(output_file=self.output_file)
            self.push_screen(export, self._handle_export_result)
        else:
            self.notify(
                "[$error bold]No scan results available. Run a scan first[/]",
                severity="error")

    def _handle_export_result(self, result):
        """Handle export result"""
        success, message, filename = result
        if success:
            self.notify(f"[$success bold]{message}[/]")
            self.results_log.clear()
            self.results_log.write(open(filename).read(), scroll_end=False)
        else:
            self.notify(f"[$error bold]{message}[/]", severity="error")

    def action_quit(self):
        """Exit application after confirmation"""
        self.push_screen(QuitModal(), self._handle_quit_confirmation)

    def _handle_quit_confirmation(self, confirmed: bool):
        """Handle the result of quit confirmation dialog"""
        if confirmed:
            self.exit()


if __name__ == "__main__":
    CardioNetApp().run()
