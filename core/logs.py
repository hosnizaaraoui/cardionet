import asyncio
from textual.widgets import RichLog


class Logs(RichLog):

    def on_mount(self):
        self.highlight = True

    async def stream_process(self, command: list[str]):
        """Run a process and stream its stdout line by line."""

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)

        # Read output line by line
        async for line in process.stdout:
            decoded = line.decode().strip()
            self.write(decoded)
            await asyncio.sleep(0)  # yield control to Textual

        await process.wait()
        self.write(f"Process finished with code {process.returncode}")

    async def scripts_stream_process(self, command: list[str]) -> list[str]:
        """Run a process, stream output, and extract script names."""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)

        script_names = []
        last_line = ""

        async for raw_line in process.stdout:
            line = raw_line.decode().strip()
            self.write(line)
            await asyncio.sleep(0)

            # Detect script header pattern:
            #   - a line with no spaces
            #   - followed by "Categories:" on next line
            if last_line and line.startswith("Categories:") and len(
                    script_names) <= 25:
                script_names.append(last_line)

            last_line = line

            await asyncio.sleep(0)

        await process.wait()
        self.write(f"\nProcess finished with code {process.returncode}")
        return script_names
