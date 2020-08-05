from abc import abstractmethod
import logging

from ._types import OutputControls, ReaderLedControls, ReaderBuzzerControl, ReaderTextOutput
from ._message import Message
import datetime

log = logging.getLogger('osdp')


class Command(Message):

	def __init__(self):
		self._address = None
		self._code = None

	@property
	def command_code(self) -> int:
		pass

	@abstractmethod
	def security_control_block(self) -> bytes:
		pass

	@abstractmethod
	def custom_command_update(self, command_buffer: bytearray):
		pass

	def build_command(self, device) -> bytes:
		command_buffer = bytearray([
			self.SOM,
			self.address,
			0x00,
			0x00,
			device.message_control.control_byte
		])

		if device.message_control.has_security_control_block:
			command_buffer.extend(self.security_control_block())

		command_buffer.append(self.command_code)

		if device.is_security_established:
			log.debug("Building secure message...")
			command_buffer.extend(self.encrypted_data(device))

			# TODO: I don't think this needed
			# include mac and crc/checksum in length before generating mac
			additional_length = 4 + (2 if device.message_control.use_crc else 1)
			self.add_packet_length(command_buffer, additional_length)

			command_buffer.extend(device.generate_mac(bytes(command_buffer), True)[0:4])
		else:
			command_buffer.extend(self.data())

		command_buffer.append(0x00)
		if device.message_control.use_crc:
			command_buffer.append(0x00)

		self.add_packet_length(command_buffer)

		if device.message_control.use_crc:
			self.add_crc(command_buffer)
		else:
			self.add_checksum(command_buffer)

		self.custom_command_update(command_buffer)

		return bytes(command_buffer)


class PollCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x60

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x15])

	def data(self) -> bytes:
		return bytes([])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class IdReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x61

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return bytes([0x00])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class DeviceCapabilitiesCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x62

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return bytes([0x00])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class LocalStatusReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x64

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x15])

	def data(self) -> bytes:
		return bytes([])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class InputStatusReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x65

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x15])

	def data(self) -> bytes:
		return bytes([])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class OutputStatusReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x66

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x15])

	def data(self) -> bytes:
		return bytes([])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ReaderStatusReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	@property
	def command_code(self) -> int:
		return 0x67

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x15])

	def data(self) -> bytes:
		return bytes([])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class OutputControlCommand(Command):

	def __init__(self, address: int, output_controls: OutputControls):
		self.address = address
		self.output_controls = output_controls

	@property
	def command_code(self) -> int:
		return 0x68

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.output_controls.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ReaderLedControlCommand(Command):

	def __init__(self, address: int, reader_led_controls: ReaderLedControls):
		self.address = address
		self.reader_led_controls = reader_led_controls

	@property
	def command_code(self) -> int:
		return 0x69

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.reader_led_controls.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ReaderBuzzerControlCommand(Command):

	def __init__(self, address: int, reader_buzzer_control: ReaderBuzzerControl):
		self.address = address
		self.reader_buzzer_control = reader_buzzer_control

	@property
	def command_code(self) -> int:
		return 0x6A

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.reader_buzzer_control.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ReaderTextOutputCommand(Command):

	def __init__(self, address: int, reader_text_output: ReaderTextOutput):
		self.address = address
		self.reader_text_output = reader_text_output

	@property
	def command_code(self) -> int:
		return 0x6B

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.reader_text_output.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass


class SetDateTimeCommand(Command):

	def __init__(self, address: int, timestamp: datetime.datetime):
		self.address = address
		self.timestamp = timestamp

	@property
	def command_code(self) -> int:
		return 0x6D

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		year_bytes = self.timestamp.year.to_bytes(2, byteorder='little')
		return bytes([
			year_bytes[0],
			year_bytes[1],
			self.timestamp.month,
			self.timestamp.day,
			self.timestamp.hour,
			self.timestamp.minute,
			self.timestamp.second
		])

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ManufacturerSpecificCommand(Command):

	def __init__(self, address: int, manufacturer_data: bytes):
		self.address = address
		self.manufacturer_data = manufacturer_data

	@property
	def command_code(self) -> int:
		return 0x80

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.manufacturer_data

	def custom_command_update(self, command_buffer: bytearray):
		pass


class SecurityInitializationRequestCommand(Command):

	def __init__(self, address: int, server_random_number: bytes):
		self.address = address
		self.server_random_number = server_random_number

	@property
	def command_code(self) -> int:
		return 0x76

	def security_control_block(self) -> bytes:
		return bytes([0x03, 0x11, 0x00])

	def data(self) -> bytes:
		return self.server_random_number

	def custom_command_update(self, command_buffer: bytearray):
		pass


class ServerCryptogramCommand(Command):

	def __init__(self, address: int, server_cryptogram: bytes):
		self.address = address
		self.server_cryptogram = server_cryptogram

	@property
	def command_code(self) -> int:
		return 0x77

	def security_control_block(self) -> bytes:
		return bytes([0x03, 0x13, 0x00])

	def data(self) -> bytes:
		return self.server_cryptogram

	def custom_command_update(self, command_buffer: bytearray):
		pass


class KeySetCommand(Command):

	def __init__(self, address: int, scbk: bytes):
		self.address = address
		self.scbk = scbk

	@property
	def command_code(self) -> int:
		return 0x75

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x17])

	def data(self) -> bytes:
		return self.keyset_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass

	def keyset_data(self):
		header = []
		type = 0x01
		length = 0x10
		scbk = [0x41, 0x02, 0x31, 0x84, 0xF1, 0xA2, 0xDE, 0x7C, 0x32, 0x98, 0x01, 0xB8, 0x7B, 0x56, 0xB3, 0x60]
		header.append(type)
		header.append(length)
		return bytes(header + scbk)
