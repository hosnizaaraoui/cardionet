import xml.etree.ElementTree as ET
from datetime import datetime


class NmapXMLParser:
    """Parse Nmap XML output and generate comprehensive text reports"""

    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.hosts = []
        self.parse_xml()

    def parse_xml(self):
        """Parse all hosts and their data from XML"""
        for host in self.root.findall('host'):
            host_data = self._parse_host(host)
            self.hosts.append(host_data)

    def _parse_host(self, host_elem):
        """Extract comprehensive host information"""
        host_info = {}

        # Host status
        status = host_elem.find('status')
        host_info['state'] = status.get(
            'state', 'unknown') if status is not None else 'unknown'
        host_info['reason'] = status.get('reason',
                                         '') if status is not None else ''

        # Host address (IPv4/IPv6)
        address = host_elem.find('address')
        host_info['addr'] = address.get(
            'addr', 'N/A') if address is not None else 'N/A'
        host_info['addrtype'] = address.get(
            'addrtype', 'ipv4') if address is not None else 'ipv4'

        # Hostnames
        hostnames_elem = host_elem.find('hostnames')
        host_info['hostnames'] = []
        if hostnames_elem is not None:
            for hostname in hostnames_elem.findall('hostname'):
                name = hostname.get('name', '')
                htype = hostname.get('type', '')
                if name:
                    host_info['hostnames'].append({
                        'name': name,
                        'type': htype
                    })

        # Ports
        ports_elem = host_elem.find('ports')
        host_info['ports'] = []
        host_info['port_stats'] = {
            'open': 0,
            'closed': 0,
            'filtered': 0,
            'other': 0
        }

        if ports_elem is not None:
            # Individual ports
            for port in ports_elem.findall('port'):
                port_info = self._parse_port(port)
                host_info['ports'].append(port_info)

                # Count port states
                state = port_info['state']
                if state == 'open':
                    host_info['port_stats']['open'] += 1
                elif state == 'closed':
                    host_info['port_stats']['closed'] += 1
                elif state == 'filtered':
                    host_info['port_stats']['filtered'] += 1
                else:
                    host_info['port_stats']['other'] += 1

            # Extra ports (condensed ports)
            for extraports in ports_elem.findall('extraports'):
                extra_info = {
                    'state': extraports.get('state', 'unknown'),
                    'count': int(extraports.get('count', 0)),
                    'reasons': []
                }
                for reason in extraports.findall('extrareasons'):
                    extra_info['reasons'].append({
                        'reason':
                        reason.get('reason', ''),
                        'count':
                        int(reason.get('count', 0))
                    })
                host_info['extraports'] = extra_info

        # OS Detection
        host_info['os'] = []
        os_elem = host_elem.find('os')
        if os_elem is not None:
            for osmatch in os_elem.findall('osmatch'):
                host_info['os'].append({
                    'name': osmatch.get('name', 'Unknown'),
                    'accuracy': osmatch.get('accuracy', '0')
                })

        # Trace (Traceroute)
        host_info['trace'] = []
        trace_elem = host_elem.find('trace')
        if trace_elem is not None:
            for hop in trace_elem.findall('hop'):
                host_info['trace'].append({
                    'ttl': hop.get('ttl', ''),
                    'host': hop.get('host', ''),
                    'ip': hop.get('ipaddr', ''),
                    'time': hop.get('time', '')
                })

        return host_info

    def _parse_port(self, port_elem):
        """Extract port information"""
        port_info = {}

        port_info['protocol'] = port_elem.get('protocol', 'tcp')
        port_info['portid'] = port_elem.get('portid', 'unknown')

        # Port state
        state = port_elem.find('state')
        if state is not None:
            port_info['state'] = state.get('state', 'unknown')
            port_info['state_reason'] = state.get('reason', '')
        else:
            port_info['state'] = 'unknown'
            port_info['state_reason'] = ''

        # Service information
        service = port_elem.find('service')
        if service is not None:
            port_info['service'] = service.get('name', 'unknown')
            port_info['product'] = service.get('product', '')
            port_info['version'] = service.get('version', '')
            port_info['extrainfo'] = service.get('extrainfo', '')
            port_info['method'] = service.get('method', '')
            port_info['conf'] = service.get('conf', '0')
        else:
            port_info['service'] = 'unknown'
            port_info['product'] = ''
            port_info['version'] = ''
            port_info['extrainfo'] = ''
            port_info['method'] = ''
            port_info['conf'] = '0'

        # Script output
        port_info['scripts'] = []
        for script in port_elem.findall('script'):
            port_info['scripts'].append({
                'id': script.get('id', ''),
                'output': script.get('output', '')
            })

        return port_info

    def generate_report(self, output_file=None):
        """Generate comprehensive text report"""
        report = self._build_report()

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)

        return report

    def _build_report(self):
        """Build the text report"""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("NMAP SCAN REPORT")
        lines.append("=" * 80)
        lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"XML File: {self.xml_file}")
        lines.append("")

        # Scan summary
        scan_args = self.root.get('args', 'N/A')
        scan_version = self.root.get('version', 'N/A')
        lines.append("SCAN INFORMATION")
        lines.append("-" * 80)
        lines.append(f"Nmap Version: {scan_version}")
        lines.append(f"Command: {scan_args}")
        lines.append(f"Total Hosts: {len(self.hosts)}")
        lines.append("")

        # Detailed host information
        for i, host in enumerate(self.hosts, 1):
            lines.extend(self._format_host(host, i))

        # Summary statistics
        lines.extend(self._format_summary())

        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_host(self, host, host_num):
        """Format individual host information"""
        lines = []

        lines.append(f"\nHOST {host_num}")
        lines.append("-" * 80)
        lines.append(f"Address: {host['addr']} ({host['addrtype']})")
        lines.append(f"Status: {host['state'].upper()} ({host['reason']})")

        # Hostnames
        if host['hostnames']:
            lines.append("Hostnames:")
            for hostname in host['hostnames']:
                lines.append(f"  {hostname['name']} ({hostname['type']})")

        # Port summary
        stats = host['port_stats']
        lines.append(f"\nPort Summary:")
        lines.append(f"  Open: {stats['open']}, Closed: {stats['closed']}, "
                     f"Filtered: {stats['filtered']}, Other: {stats['other']}")

        # Open ports (most important)
        open_ports = [p for p in host['ports'] if p['state'] == 'open']
        if open_ports:
            lines.append(f"\nOPEN PORTS ({len(open_ports)}):")
            for port in sorted(open_ports, key=lambda x: int(x['portid'])):
                lines.append(self._format_port(port))

        # Filtered ports
        filtered_ports = [p for p in host['ports'] if p['state'] == 'filtered']
        if filtered_ports:
            lines.append(f"\nFILTERED PORTS ({len(filtered_ports)}):")
            for port in sorted(filtered_ports,
                               key=lambda x: int(x['portid']))[:10]:
                lines.append(self._format_port(port))
            if len(filtered_ports) > 10:
                lines.append(
                    f"  ... and {len(filtered_ports) - 10} more filtered ports"
                )

        # Closed ports
        closed_ports = [p for p in host['ports'] if p['state'] == 'closed']
        if closed_ports and len(closed_ports) <= 10:
            lines.append(f"\nCLOSED PORTS ({len(closed_ports)}):")
            for port in sorted(closed_ports, key=lambda x: int(x['portid'])):
                lines.append(self._format_port(port))
        elif closed_ports:
            lines.append(f"\nCLOSED PORTS: {len(closed_ports)} ports closed")

        # Extra ports summary
        if 'extraports' in host:
            extra = host['extraports']
            lines.append(
                f"\nEXTRA PORTS: {extra['count']} ports {extra['state']}")
            for reason in extra['reasons']:
                lines.append(f"  {reason['reason']}: {reason['count']}")

        # OS Detection
        if host['os']:
            lines.append(f"\nOS DETECTION:")
            for os_match in host['os'][:3]:
                lines.append(f"  {os_match['name']} ({os_match['accuracy']}%)")

        # Traceroute
        if host['trace']:
            lines.append(f"\nTRACEROUTE:")
            for hop in host['trace']:
                lines.append(
                    f"  TTL {hop['ttl']}: {hop['host']} ({hop['ip']}) "
                    f"- {hop['time']}ms")

        return lines

    def _format_port(self, port):
        """Format port information"""
        portid = port['portid']
        protocol = port['protocol']
        state = port['state']
        service = port['service']
        version = port['version']
        product = port['product']

        # Build port line
        port_line = f"  {portid}/{protocol:3} {state:8} {service:15}"

        # Add version info if available
        if product or version:
            port_line += f" {product}"
            if version:
                port_line += f" {version}"

        # Add extra info if available
        if port['extrainfo']:
            port_line += f" ({port['extrainfo']})"

        return port_line

    def _format_summary(self):
        """Format scan summary statistics"""
        lines = []

        lines.append("\n" + "=" * 80)
        lines.append("SCAN SUMMARY")
        lines.append("=" * 80)

        total_open = sum(h['port_stats']['open'] for h in self.hosts)
        total_closed = sum(h['port_stats']['closed'] for h in self.hosts)
        total_filtered = sum(h['port_stats']['filtered'] for h in self.hosts)

        lines.append(f"Total Hosts Scanned: {len(self.hosts)}")
        hosts_up = sum(1 for h in self.hosts if h['state'] == 'up')
        lines.append(f"Hosts Up: {hosts_up}")
        lines.append(f"\nPort Statistics (All Hosts):")
        lines.append(f"  Total Open: {total_open}")
        lines.append(f"  Total Closed: {total_closed}")
        lines.append(f"  Total Filtered: {total_filtered}")

        return lines


# Usage example
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <xml_file> [output_file]")
        sys.exit(1)

    xml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        parser = NmapXMLParser(xml_file)
        report = parser.generate_report(output_file)
        print(report)

        if output_file:
            print(f"\nReport saved to: {output_file}")
    except Exception as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)
