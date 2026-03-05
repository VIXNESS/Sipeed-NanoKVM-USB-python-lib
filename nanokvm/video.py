"""
Video capture from NanoKVM-USB's UVC (USB Video Class) device using OpenCV.

The NanoKVM-USB exposes HDMI input as a standard USB camera. This module
wraps OpenCV's VideoCapture for convenient frame grabbing, suitable for
feeding into AI vision models.
"""

from __future__ import annotations

import base64
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray


class VideoCapture:
    def __init__(self) -> None:
        self._cap: cv2.VideoCapture | None = None

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def open(
        self,
        device: int | str = 0,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
    ) -> None:
        """
        Open a UVC video device.

        Args:
            device: Device index (int) or device path (str).
            width: Requested capture width.
            height: Requested capture height.
            fps: Requested frame rate.
        """
        if self._cap is not None:
            self.close()

        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise ConnectionError(f"Cannot open video device: {device}")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        self._cap = cap

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def read_frame(self) -> NDArray[np.uint8]:
        """
        Capture a single frame.

        Returns:
            BGR numpy array of shape (height, width, 3).

        Raises:
            ConnectionError: If the device is not open or the read fails.
        """
        if self._cap is None or not self._cap.isOpened():
            raise ConnectionError("Video device not open")

        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise ConnectionError("Failed to read frame from video device")

        return np.asarray(frame, dtype=np.uint8)

    def read_frame_rgb(self) -> NDArray[np.uint8]:
        """Capture a frame and convert BGR -> RGB."""
        frame = self.read_frame()
        return np.asarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), dtype=np.uint8)

    def read_frame_jpeg(self, quality: int = 85) -> bytes:
        """
        Capture a frame and encode as JPEG bytes.

        Args:
            quality: JPEG quality (0-100).
        """
        frame = self.read_frame()
        ok, buf = cv2.imencode(".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, quality))
        if not ok:
            raise RuntimeError("JPEG encoding failed")
        return buf.tobytes()

    def read_frame_base64(self, quality: int = 85) -> str:
        """
        Capture a frame and return as a base64-encoded JPEG string.
        Useful for sending directly to multimodal LLM APIs.
        """
        jpeg_bytes = self.read_frame_jpeg(quality)
        return base64.b64encode(jpeg_bytes).decode("ascii")

    def get_resolution(self) -> tuple[int, int]:
        """Return current (width, height) of the capture."""
        if self._cap is None:
            raise ConnectionError("Video device not open")
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return w, h

    def get_fps(self) -> float:
        if self._cap is None:
            raise ConnectionError("Video device not open")
        return self._cap.get(cv2.CAP_PROP_FPS)

    @staticmethod
    def list_devices(max_index: int = 10) -> list[dict[str, Any]]:
        """
        Probe video device indices 0..max_index and return info for each available one.
        Useful for finding which index corresponds to the NanoKVM UVC device.
        """
        devices: list[dict[str, Any]] = []
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                devices.append({
                    "index": i,
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    "fps": cap.get(cv2.CAP_PROP_FPS),
                    "backend": cap.getBackendName(),
                })
                cap.release()
        return devices

    def __enter__(self) -> VideoCapture:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
