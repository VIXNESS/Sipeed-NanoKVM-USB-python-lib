from __future__ import annotations

import pytest

from nanokvm.protocol import CmdEvent, CmdPacket, HEAD1, HEAD2, InfoPacket


class TestCmdPacketEncode:
    def test_empty_data(self) -> None:
        pkt = CmdPacket(addr=0x00, cmd=CmdEvent.GET_INFO, data=[])
        encoded = pkt.encode()
        assert encoded[0] == HEAD1
        assert encoded[1] == HEAD2
        assert encoded[2] == 0x00  # addr
        assert encoded[3] == CmdEvent.GET_INFO  # cmd
        assert encoded[4] == 0  # length
        checksum = sum(encoded[:-1]) & 0xFF
        assert encoded[-1] == checksum

    def test_with_data(self) -> None:
        pkt = CmdPacket(addr=0x01, cmd=0x02, data=[0x10, 0x20, 0x30])
        encoded = pkt.encode()
        assert encoded[4] == 3  # length
        assert list(encoded[5:8]) == [0x10, 0x20, 0x30]
        checksum = sum(encoded[:-1]) & 0xFF
        assert encoded[-1] == checksum

    def test_header_bytes(self) -> None:
        pkt = CmdPacket()
        encoded = pkt.encode()
        assert encoded[0] == 0x57
        assert encoded[1] == 0xAB


class TestCmdPacketDecode:
    def test_roundtrip(self) -> None:
        original = CmdPacket(addr=0x05, cmd=0x02, data=[0xAA, 0xBB])
        encoded = original.encode()
        decoded = CmdPacket.decode(encoded)
        assert decoded.addr == original.addr
        assert decoded.cmd == original.cmd
        assert decoded.data == original.data

    def test_roundtrip_empty_data(self) -> None:
        original = CmdPacket(addr=0x00, cmd=CmdEvent.GET_INFO, data=[])
        decoded = CmdPacket.decode(original.encode())
        assert decoded.addr == 0x00
        assert decoded.cmd == CmdEvent.GET_INFO
        assert decoded.data == []

    def test_missing_header_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot find packet header"):
            CmdPacket.decode([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def test_truncated_packet_raises(self) -> None:
        with pytest.raises(ValueError, match="Packet too short"):
            CmdPacket.decode([HEAD1, HEAD2, 0x00, 0x01])

    def test_checksum_mismatch_raises(self) -> None:
        pkt = CmdPacket(addr=0x00, cmd=0x01, data=[0x10])
        encoded = bytearray(pkt.encode())
        encoded[-1] ^= 0xFF  # corrupt checksum
        with pytest.raises(ValueError, match="Checksum mismatch"):
            CmdPacket.decode(encoded)

    def test_data_length_mismatch_raises(self) -> None:
        raw = [HEAD1, HEAD2, 0x00, 0x01, 0x05, 0x10, 0x00]
        with pytest.raises(ValueError, match="truncated"):
            CmdPacket.decode(raw)

    def test_leading_garbage(self) -> None:
        """Decoder should skip bytes before the header."""
        original = CmdPacket(addr=0x00, cmd=0x01, data=[0x42])
        encoded = original.encode()
        with_garbage = bytes([0xFF, 0xFE, 0xFD]) + encoded
        decoded = CmdPacket.decode(with_garbage)
        assert decoded.cmd == 0x01
        assert decoded.data == [0x42]


class TestInfoPacket:
    def test_basic_parsing(self) -> None:
        # version byte 0x30 -> V1.0, connected, no locks
        info = InfoPacket.from_data([0x30, 0x01, 0x00])
        assert info.chip_version == "V1.0"
        assert info.is_connected is True
        assert info.num_lock is False
        assert info.caps_lock is False
        assert info.scroll_lock is False

    def test_version_parsing(self) -> None:
        info = InfoPacket.from_data([0x35, 0x00, 0x00])
        assert info.chip_version == "V1.5"

    def test_disconnected(self) -> None:
        info = InfoPacket.from_data([0x30, 0x00, 0x00])
        assert info.is_connected is False

    def test_num_lock(self) -> None:
        info = InfoPacket.from_data([0x30, 0x01, 0x01])
        assert info.num_lock is True
        assert info.caps_lock is False
        assert info.scroll_lock is False

    def test_caps_lock(self) -> None:
        info = InfoPacket.from_data([0x30, 0x01, 0x02])
        assert info.num_lock is False
        assert info.caps_lock is True
        assert info.scroll_lock is False

    def test_scroll_lock(self) -> None:
        info = InfoPacket.from_data([0x30, 0x01, 0x04])
        assert info.num_lock is False
        assert info.caps_lock is False
        assert info.scroll_lock is True

    def test_all_locks(self) -> None:
        info = InfoPacket.from_data([0x30, 0x01, 0x07])
        assert info.num_lock is True
        assert info.caps_lock is True
        assert info.scroll_lock is True

    def test_minimal_data(self) -> None:
        """Only version byte provided."""
        info = InfoPacket.from_data([0x30])
        assert info.chip_version == "V1.0"
        assert info.is_connected is False
        assert info.num_lock is False

    def test_empty_data_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid version byte"):
            InfoPacket.from_data([])

    def test_invalid_version_byte_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid version byte"):
            InfoPacket.from_data([0x10])
