from abc import ABC, abstractmethod 
from message import Message

class Command(Message):

	def __init__(self):
		self._address = None
		self._code = None

	@property
	@abstractmethod
	def command_code(self) -> int:
		pass

	@abstractmethod
	def security_control_block(self) -> bytes:
		pass

	@abstractmethod
	def custom_command_update(self, command_buffer: bytearray):
		pass

	def build_command(self, device: Device) -> bytes:
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
			command_buffer.extend(self.encrypted_data(device))

			# TODO: I don't think this needed
			# include mac and crc/checksum in length before generating mac
			# additional_length = 4 + (device.message_control.use_crc ? 2 : 1)
			# self.add_packet_length(command_buffer, additional_length)

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

		custom_command_update(command_buffer)

		return bytes(command_buffer)
