from pathlib import Path
import shutil
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, Grid, VerticalScroll
from textual.widgets import Static, Button, Input, Select, Label, Checkbox
from core.nmap_parsers import NmapXMLParser
from core.logs import Logs
from textual import on
from textual.events import Key


class QuitModal(ModalScreen):
    """
    Confirmation dialog for safely exiting the application.
    
    Displays a confirmation prompt asking the user to confirm they want to quit.
    Provides 'Yes' and 'No' buttons for user confirmation. Also supports keyboard
    shortcuts: 'Y' for yes, any other key for no.
    
    Returns:
        bool: True if user confirms quit, False if cancelled.
    """

    def compose(self):
        with Vertical():
            yield Label("[bold]Do you want to quit?[/]")
            with Horizontal():
                yield Button("Yes", id="yes", classes="success")
                yield Button("No", id="no", classes="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss(True)

        else:
            self.dismiss(False)

    def on_key(self, event: Key):
        if event.key.lower() == "y":
            self.dismiss(True)

        else:
            self.dismiss(False)


class ExportModal(ModalScreen):
    """
    File export dialog with optional XML parsing.
    
    Allows users to export scan results to a file with two options:
    - Raw export: Copies the raw output file (XML, Grepable, or Normal)
    - Parsed export (XML only): Parses XML into a formatted readable text report
    
    Auto-detects file type and adds appropriate extensions. Normal output is
    always saved alongside chosen format for comprehensive logging.
    
    Attributes:
        output_file: Path to the source scan output file
        parsing: Checkbox to enable/disable XML parsing (only for XML files)
        filename: Input field for destination filename
    
    Returns:
        tuple: (success: bool, message: str, filepath: str)
    """

    def __init__(self,
                 name=None,
                 id=None,
                 classes=None,
                 output_file: str = ""):
        super().__init__(name, id, classes)
        self.output_file = output_file
        self.filename = Input(placeholder="Enter filename or path")

        # Checkbox enabled only if output file is XML
        is_xml = output_file.endswith('.xml')
        self.parsing = Checkbox(id="parsing", disabled=not is_xml)

    def compose(self):
        with Vertical():
            yield Label("[bold]Export Scan Results[/]")

            # Show source file info
            yield Static(f"Source: {Path(self.output_file).name}",
                         classes="muted")

            # Filename input
            with Vertical():
                yield Label("Export as:")
                yield self.filename

            # Parsing option (only for XML)
            if self.output_file.endswith('.xml'):
                with Horizontal(classes="h3"):
                    yield self.parsing
                    yield Static("Parse to readable format")

            # Buttons
            with Horizontal():
                yield Button("Save", id="save", classes="success")
                yield Button("Cancel", id="cancel", classes="error")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            try:
                final_path = self.handle_export()
                self.dismiss((True, "Export successful!", final_path))
            except Exception as e:
                self.dismiss((False, f"Export failed: {str(e)}", ""))
        else:
            self.dismiss((False, "Export cancelled", ""))

    def handle_export(self):
        """Handle file export with optional XML parsing"""
        export_filename = self.filename.value.strip()

        if not export_filename:
            raise ValueError("Filename cannot be empty")

        # Add .txt extension if parsing XML, otherwise keep original extension
        if self.output_file.endswith('.xml') and self.parsing.value:
            # Parse XML and save as text
            if not export_filename.endswith('.txt'):
                export_filename += '.txt'

            final_path = self._export_parsed_xml(export_filename)
        else:
            # Just copy the raw file
            final_path = self._export_raw_file(export_filename)

        # Return the final filename with path
        return final_path

    def _export_parsed_xml(self, output_path: str) -> str:
        """Parse XML file and save as formatted text"""
        try:
            # Parse XML
            parser = NmapXMLParser(self.output_file)

            # Generate report
            report = parser.generate_report()

            # Write to file
            with open(output_path, 'w') as f:
                f.write(report)

            return output_path

        except Exception as e:
            raise Exception(f"XML Parsing Error: {str(e)}")

    def _export_raw_file(self, output_path: str) -> str:
        """Copy raw output file to destination"""
        try:
            # Determine file extension based on source
            if not Path(output_path).suffix:
                if self.output_file.endswith('.xml'):
                    output_path += '.xml'
                elif self.output_file.endswith('.gnmap'):
                    output_path += '.gnmap'
                else:
                    output_path += '.txt'

            # Copy file
            shutil.copy(self.output_file, output_path)

            return output_path

        except Exception as e:
            raise Exception(f"File Copy Error: {str(e)}")


class ExtraModal(ModalScreen):
    """
    Modal for advanced scanning options.
    
    Allows users to enable/disable extra scanning features:
    - OS Detection (-O): Attempt to identify operating systems
    - Version Detection (-sV): Probe open ports for service versions
    - Verbose Mode (-vv): Print detailed information during scan
    
    All options are presented as checkboxes for easy toggling.
    
    Returns:
        list: [verbose_enabled, os_detection_enabled, version_detection_enabled]
    """

    verbose = Checkbox(id="verbose")
    version_detection = Checkbox(id="version")
    os = Checkbox(id="os")

    def compose(self):
        with Vertical():
            yield Label("[bold]Extra Options[/]")
            with Grid(classes="extras-options"):
                with Horizontal():
                    yield Static("OS")
                    yield self.os
                with Horizontal():
                    yield Static("Version Detection")
                    yield self.version_detection
                with Horizontal():
                    yield Static("Verbose")
                    yield self.verbose
                yield Button("Apply", id="apply", classes="success")

    def on_button_pressed(self):
        self.dismiss(
            [self.verbose.value, self.os.value, self.version_detection.value])


class ScriptsModal(ModalScreen):
    """
    Interactive nmap NSE script selector and viewer.
    
    Provides filtering and browsing of nmap's script library. Users can:
    - Filter scripts by pattern (e.g., 'ftp-*', 'ssl-*')
    - View filtered script list in a searchable dropdown
    - Display detailed script descriptions and outputs
    - Apply selected script to the scan configuration
    
    Automatically parses script metadata from nmap --script-help output.
    
    Returns:
        str: Selected script name, or empty string if cancelled.
    """

    def compose(self):
        self.filter_words = Input(placeholder="ftp-*", id="filter_words")
        self.filtered_scripts = Select(options=[],
                                       id="filtered_scripts",
                                       type_to_search=True)
        self.script_chosen = Logs(id="script_description")

        with Grid(classes="LR"):
            with VerticalScroll():
                yield Label("[bold]Nmap Scripts[/]")
                with Horizontal():
                    yield Static("Filter")
                    yield self.filter_words
                    yield Button("Filter", id="filter")

                with Horizontal():
                    yield Static("Filtered")
                    yield self.filtered_scripts

                with Horizontal():
                    yield Button("Apply", id="apply", classes="success")
                    yield Button("Cancel", id="cancel")

            yield self.script_chosen

    @on(Input.Submitted)
    def apply_filter(self):
        self.run_worker(self.filter_scripts(), exclusive=True)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "apply":
            if self.filtered_scripts.selection:
                self.dismiss(self.filtered_scripts.value)

        elif event.button.id == "filter":
            self.run_worker(self.filter_scripts(), exclusive=True)

        else:
            self.dismiss()

    async def filter_scripts(self):
        """Run nmap and populate Select with script names."""
        self.script_chosen.clear()

        command = ["nmap", "--script-help", self.filter_words.value]
        scripts = await self.script_chosen.scripts_stream_process(command)

        # Update the select widget
        options = [(s, s) for s in scripts]
        self.filtered_scripts.set_options(options)

    @on(Select.Changed)
    async def filter_script_by_name(self):
        """Run nmap and populate Select with script names."""
        self.script_chosen.clear()
        command = ["nmap", "--script-help", self.filtered_scripts.value]
        await self.script_chosen.scripts_stream_process(command)
