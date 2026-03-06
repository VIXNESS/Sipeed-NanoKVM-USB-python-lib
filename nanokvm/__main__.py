"""Quick CLI to list available NanoKVM devices and test connectivity."""

from nanokvm import SerialConnection, VideoCapture
from nanokvm._logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("=== Available Serial Ports ===")
    ports = SerialConnection.list_ports()
    if ports:
        for p in ports:
            logger.info(f"  {p.device}: {p.description} [{p.hwid}]")
    else:
        logger.info("  (none found)")

    logger.info("\n=== Available Video Devices ===")
    devices = VideoCapture.list_devices()
    if devices:
        for d in devices:
            logger.info(
                f"  Index {d['index']}: {d['width']}x{d['height']} @ {d['fps']}fps ({d['backend']})"
            )
    else:
        logger.info("  (none found)")


if __name__ == "__main__":
    main()
