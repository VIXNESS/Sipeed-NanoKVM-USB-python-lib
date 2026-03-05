"""Quick CLI to list available NanoKVM devices and test connectivity."""

from nanokvm import SerialConnection, VideoCapture


def main() -> None:
    print("=== Available Serial Ports ===")
    ports = SerialConnection.list_ports()
    if ports:
        for p in ports:
            print(f"  {p.device}: {p.description} [{p.hwid}]")
    else:
        print("  (none found)")

    print("\n=== Available Video Devices ===")
    devices = VideoCapture.list_devices()
    if devices:
        for d in devices:
            print(f"  Index {d['index']}: {d['width']}x{d['height']} @ {d['fps']}fps ({d['backend']})")
    else:
        print("  (none found)")


if __name__ == "__main__":
    main()
