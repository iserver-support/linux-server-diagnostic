import argparse
import json

from .checks import (
    check_failed_services,
    check_filesystem,
    check_listening_ports,
    check_memory,
    check_system,
)


def main():
    parser = argparse.ArgumentParser(
        description="Linux server diagnostic utility"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )

    args = parser.parse_args()

    report = {
        "system": check_system(),
        "memory": check_memory(),
        "filesystem": check_filesystem("/"),
        "failed_services": check_failed_services(),
        "listening_ports": check_listening_ports(),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    system = report["system"]
    memory = report["memory"]
    filesystem = report["filesystem"]

    print("Linux Server Diagnostic")
    print("=" * 28)

    print(f"Hostname:       {system['hostname']}")
    print(f"Uptime:         {system['uptime']}")
    print(f"CPU count:      {system['cpu_count']}")

    if system["load_average"]:
        print(
            "Load average:   "
            f"{system['load_average'][0]:.2f} "
            f"{system['load_average'][1]:.2f} "
            f"{system['load_average'][2]:.2f}"
        )

    print()
    print("Memory")
    print("-" * 28)
    print(f"Total:          {memory.get('total_mb', 0):.0f} MB")
    print(f"Available:      {memory.get('available_mb', 0):.0f} MB")
    print(f"Used:           {memory.get('used_percent', 0):.1f}%")
    print(f"Swap total:     {memory.get('swap_total_mb', 0):.0f} MB")

    print()
    print("Root filesystem")
    print("-" * 28)
    print(f"Size:           {filesystem.get('size_gb', 0):.2f} GB")
    print(f"Used:           {filesystem.get('used_percent', 0):.1f}%")
    print(
        "Inodes used:    "
        f"{filesystem.get('inode_used_percent', 0):.1f}%"
    )

    failed = report["failed_services"]

    print()
    print("Systemd")
    print("-" * 28)

    if failed.get("available"):
        print(f"Failed units:   {failed['failed_count']}")

        for service in failed["services"]:
            print(f"  - {service}")
    else:
        print(f"Unavailable:    {failed.get('reason', 'unknown')}")

    ports = report["listening_ports"]

    print()
    print("Listening sockets")
    print("-" * 28)

    if ports.get("available"):
        for socket_info in ports["sockets"]:
            print(socket_info)
    else:
        print(f"Unavailable:    {ports.get('reason', 'unknown')}")


if __name__ == "__main__":
    main()
