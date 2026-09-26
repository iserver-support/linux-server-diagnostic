# Linux Server Diagnostic

A practical Linux server diagnostic CLI for quickly checking system health,
resource utilization, filesystem capacity, inode usage, failed systemd
services, and listening network sockets.

The tool is designed for Linux system administrators, DevOps engineers,
hosting administrators, and infrastructure teams who need a lightweight
diagnostic report directly from the command line.

## Features

- Hostname and uptime detection
- CPU count and load-average reporting
- Memory and swap utilization
- Root filesystem capacity
- Filesystem inode utilization
- Failed systemd services
- Listening TCP and UDP sockets
- Human-readable terminal output
- JSON output for automation and monitoring
- No external API or cloud service required

## Requirements

- Linux
- Python 3.9 or newer
- Access to `/proc` for memory information
- `systemctl` for systemd service checks
- `ss` for listening socket detection

Some checks gracefully report as unavailable when the corresponding
Linux utility or subsystem is not present.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/linux-server-diagnostic.git
cd linux-server-diagnostic
````

Run the diagnostic tool:

```bash
python3 -m linux_server_diag
```

## Example

```text
Linux Server Diagnostic
============================

Hostname:       server01
Uptime:         up 12 days, 4 hours
CPU count:      8
Load average:   0.42 0.38 0.31

Memory
----------------------------
Total:          16384 MB
Available:      11240 MB
Used:           31.4%
Swap total:     4096 MB

Root filesystem
----------------------------
Size:           100.00 GB
Used:           47.2%
Inodes used:    12.8%

Systemd
----------------------------
Failed units:   0

Listening sockets
----------------------------
tcp LISTEN 0 128 0.0.0.0:22
tcp LISTEN 0 511 0.0.0.0:80
tcp LISTEN 0 511 0.0.0.0:443
```

The exact output depends on the Linux distribution, services, network
configuration, and resources available on the server.

## JSON Output

For automation, monitoring, or integration with another script, use:

```bash
python3 -m linux_server_diag --json
```

Example:

```json
{
  "system": {
    "hostname": "server01",
    "cpu_count": 8
  },
  "memory": {
    "total_mb": 16384,
    "available_mb": 11240,
    "used_percent": 31.4
  }
}
```

JSON output is useful when the diagnostic information needs to be processed
by shell scripts, Python applications, monitoring systems, or configuration
management tools.

## What the Checks Mean

### Load Average

Linux reports load averages over 1, 5, and 15 minutes.

Load average should not be interpreted as a simple CPU-percentage value.
For example, a load of `8` can represent very different conditions on a
2-core server compared with an 8-core server.

High load should therefore be investigated together with CPU utilization,
I/O wait, memory pressure, and running processes.

### Memory

The tool uses `/proc/meminfo` and reports available memory rather than
treating all filesystem cache as unavailable memory.

This is important because Linux intentionally uses otherwise-unused memory
for caching.

### Filesystem Usage

Disk utilization is checked using filesystem statistics rather than parsing
the output of `df` with fragile text processing.

Both storage capacity and inode utilization are reported.

A filesystem can have free gigabytes while still being unable to create
files because its inode allocation is exhausted.

### Failed Services

When systemd is available, the tool checks for failed units using:

```bash
systemctl --failed
```

A failed service does not automatically mean the server is unhealthy, but it
is an important diagnostic signal that should be investigated.

### Listening Sockets

The tool uses `ss` to identify listening TCP and UDP sockets.

This can help administrators identify services exposed on the server and
compare the current listening ports against the expected configuration.

## Troubleshooting

### Permission-related information

Some Linux information may be restricted depending on the operating system,
container environment, security policy, or user privileges.

Run the diagnostic as an appropriate administrative user when deeper system
information is required.

### systemctl unavailable

Containers and non-systemd environments may not provide `systemctl`.

The tool reports this condition instead of treating it as a fatal error.

### /proc unavailable

The memory collector relies on Linux `/proc` information. Environments
without `/proc` cannot provide those memory statistics.

### ss unavailable

The listening-socket check requires the `ss` utility. Install the package
providing `ss` for your Linux distribution if this functionality is needed.

## Using the Tool During Incident Response

This utility can be useful as an initial information-gathering step during
Linux server troubleshooting.

For example:

```bash
python3 -m linux_server_diag
```

Then investigate suspicious results with standard Linux tools:

```bash
uptime
top
free -h
df -h
df -ih
systemctl --failed
ss -lntup
journalctl -p warning -b
```

The diagnostic tool does not attempt to automatically modify services,
firewall rules, processes, or configuration files. This makes it suitable
for initial inspection without introducing remediation changes.

## Automation

The JSON output can be consumed by shell scripts or Python:

```bash
python3 -m linux_server_diag --json > server-health.json
```

For example:

```bash
if python3 -m linux_server_diag --json > server-health.json; then
    echo "Diagnostic collection completed"
else
    echo "Diagnostic collection failed" >&2
    exit 1
fi
```

## Security Considerations

The tool is intended for systems that you own or are authorized to
administer.

It does not intentionally transmit diagnostic information to an external
service.

Review JSON reports before sharing them publicly because hostname,
filesystem, service, and network information may reveal details about your
infrastructure.

## Development

Run the test suite with:

```bash
pytest -v
```

Check Python compilation:

```bash
python3 -m compileall linux_server_diag
```

## Project Structure

```text
linux-server-diagnostic/
├── linux_server_diag/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── checks.py
├── tests/
│   └── test_checks.py
├── README.md
├── LICENSE
└── .gitignore
```

## Linux Server Operations

A diagnostic utility is useful for collecting information during
troubleshooting, but production infrastructure also requires ongoing
monitoring, maintenance, security updates, performance analysis, and
incident response.

For organizations that need professional [Linux server
management](https://iserversupport.com/linux-server-management/), iServerSupport
provides ongoing Linux infrastructure administration and operational support.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for
details.

## Contributing

Contributions are welcome.

When submitting a pull request:

1. Explain the problem being solved.
2. Keep the diagnostic checks focused and portable.
3. Avoid distribution-specific assumptions where possible.
4. Add tests for new functionality.
5. Do not introduce external telemetry without clearly documenting it.
6. Preserve the tool's read-only diagnostic behavior.

