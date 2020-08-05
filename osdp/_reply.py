from abc import abstractmethod
import logging
from uuid import UUID

from ._types import SecurityBlockType, ReplyType, Control
from ._message import Message
from ._command import Command
from ._device import Device

log = logging.getLogger('osdp')


class Reply(Message):

	ADDRESS_MASK = 0x7F
	REPLY_MESSAGE_HEADER_SIZE = 5
	REPLY_TYPE_INDEX = 5
	MAC_SIZE = 4
	SecureSessionMessages = [
		SecurityBlockType.CommandMessageWithNoDataSecurity.value,
		SecurityBlockType.ReplyMessageWithNoDataSecurity.value,
		SecurityBlockType.CommandMessageWithDataSecurity.value,
		SecurityBlockType.ReplyMessageWithDataSecurity.value
	]

	def __init__(self, data: bytes, connection_id: UUID, issuing_command: Command, device: Device):
		self._address = data[1] & self.ADDRESS_MASK
		self._sequence = data[4] & 0x03

		is_using_crc = (data[4] & 0x04) != 0
		reply_message_footer_size = 2 if is_using_crc else 1

		is_secure_control_block_present = (data[4] & 0x08) != 0
		secure_block_size = (data[5] & 0xFF) if is_secure_control_block_present else 0
		self._security_block_type = (data[6] & 0xFF) if is_secure_control_block_present else 0
		if is_secure_control_block_present:
			self._secure_block_data = data[(self.REPLY_MESSAGE_HEADER_SIZE + 2):][:(secure_block_size - 2)]
		else:
			self._secure_block_data = b''

		mac_size = self.MAC_SIZE if self.is_secure_message else 0
		message_length = len(data) - (reply_message_footer_size + mac_size)

		self._mac = data[message_length:][:mac_size]
		self._type = ReplyType(data[self.REPLY_TYPE_INDEX + secure_block_size] & 0xFF)

		data_start = self.REPLY_MESSAGE_HEADER_SIZE + secure_block_size + 1
		data_end = - reply_message_footer_size - mac_size
		self._extract_reply_data = data[data_start:data_end]

		if self.security_block_type == SecurityBlockType.ReplyMessageWithDataSecurity.value:
			self._extract_reply_data = self.decrypt_data(device)

		if is_using_crc:
			self._is_data_correct = self.calculate_crc(data[:-2]) == int.from_bytes(data[-2:], byteorder='little')
		else:
			self._is_data_correct = self.calculate_checksum(data[:-1]) == int.from_bytes(data[-1:], byteorder='little')

		self._message_for_mac_generation = data[:message_length]

		self._connection_id = connection_id
		self._issuing_command = issuing_command

	@property
	def security_block_type(self) -> int:
		return self._security_block_type

	@property
	def secure_block_data(self) -> bytes:
		return self._secure_block_data

	@property
	def mac(self) -> bytes:
		return self._mac

	@property
	def is_data_correct(self) -> bool:
		return self._is_data_correct

	@property
	def sequence(self) -> int:
		return self._sequence

	@property
	def is_correct_address(self) -> bool:
		return self._issuing_command.address == self.address

	@property
	def type(self) -> ReplyType:
		return self._type

	@property
	def extract_reply_data(self) -> bytes:
		return self._extract_reply_data

	@property
	def message_for_mac_generation(self) -> bytes:
		return self._message_for_mac_generation

	@property
	def is_secure_message(self) -> bool:
		return self.security_block_type in self.SecureSessionMessages

	@property
	def reply_code(self) -> int:
		pass

	@property
	def is_valid_reply(self) -> bool:
		return self.is_correct_address and self.is_data_correct

	@staticmethod
	def parse(data: bytes, connection_id: UUID, issuing_command: Command, device: Device):
		reply = UnknownReply(data, connection_id, issuing_command, device)
		return reply

	def secure_cryptogram_has_been_accepted(self) -> bool:
		log.debug("Secure block data: %s", self.secure_block_data[0])
		return self.secure_block_data[0] != 0

	def match_issuing_command(self, command: Command) -> bool:
		return command == self._issuing_command

	def is_valid_mac(self, mac: bytes) -> bool:
		return mac[:self.MAC_SIZE] == self.mac

	def build_reply(self, address: int, control: Control) -> bytes:
		command_buffer = bytearray([
			self.SOM,
			(self.address | 0x80),
			0x00,
			0x00,
			control.control_byte
		])

		if control.has_security_control_block:
			command_buffer.extend(self.security_control_block())

		command_buffer.append(self.reply_code)
		command_buffer.extend(self.data())

		command_buffer.append(0x00)
		if control.use_crc:
			command_buffer.append(0x00)
		self.add_packet_length(command_buffer)

		if control.use_crc:
			self.add_crc(command_buffer)
		else:
			self.add_checksum(command_buffer)

		return bytes(command_buffer)

	@abstractmethod
	def security_control_block(self) -> bytes:
		pass

	def __repr__(self):
		return "Connection ID: {0} Address: {1} Type: {2}".format(self._connection_id, self.address, self.type)

	def decrypt_data(self, device: Device) -> bytes:
		log.debug("Extract reply data: %s", self.extract_reply_data.hex())
		return device.decrypt_data(self.extract_reply_data)


class AckReply(Reply):

	@property
	def reply_code(self) -> int:
		return 0x40

	def security_control_block(self) -> bytes:
		return bytes([0x02, 0x16])

	def data(self) -> bytes:
		return bytes([])


class UnknownReply(Reply):

	def __init__(self, data: bytes, connection_id: UUID, issuing_command: Command, device: Device):
		super().__init__(data, connection_id, issuing_command, device)

	@property
	def reply_code(self) -> int:
		return self.type.value

	def security_control_block(self) -> bytes:
		security_block_length = len(self.secure_block_data) + 2
		secbk = bytearray([self.security_block_type, security_block_length])
		secbk.extend(self.secure_block_data)
		return bytes(secbk)

	def data(self) -> bytes:
		return self.extract_reply_data
