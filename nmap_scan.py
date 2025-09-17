import subprocess

class NmapScanner:
    def __init__(self):
        self.process = None  # Track the Nmap process

    def run_scan(self, target, scan_type="SYN", port_range="", stop_flag=None, live_callback=None):
        arguments = ""

        if scan_type == "SYN":
            arguments = "-sS"
        elif scan_type == "SYN + OS + Version":
            arguments = "-sS -O -sV"
        elif scan_type == "Aggressive":
            arguments = "-A"

        if port_range:
            arguments += f" -p {port_range}"

        # Use stdbuf to allow real-time output
        cmd = f"stdbuf -oL nmap {arguments} {target}"

        try:
            self.process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            output_lines = []

            for line in iter(self.process.stdout.readline, ''):
                if stop_flag and stop_flag[0]:
                    if self.process:
                        self.process.terminate()
                    return "Scan cancelled by user.\n"

                output_lines.append(line)

                if live_callback:
                    live_callback(line)  # Stream line immediately to GUI

            self.process.stdout.close()
            self.process.wait()

            return "".join(output_lines)

        except subprocess.TimeoutExpired:
            return "Scan timed out.\n"
        except Exception as e:
            return f"Error running scan: {str(e)}\n"
