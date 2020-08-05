import logging
import queue
import datetime

from ._types import Control
from ._command import (
	PollCommand, SecurityInitializationRequestCommand, ServerCryptogramCommand
)
from ._secure_channel import SecureChannel

log = logging.getLogger('osdp')


class Device(object):

	def __init__(self, address: int, use_crc: bool, use_secure_channel: bool):
		self._use_secure_channel = use_secure_channel
		self.address = address
		self.message_control = Control(0, use_crc, use_secure_channel)

		self._commands = queue.Queue()
		self._secure_channel = SecureChannel()
		self._last_valid_reply = datetime.datetime.utcfromtimestamp(0)

	@property
	def is_security_established(self) -> bool:
		return self.message_control.has_security_control_block and self._secure_channel.is_established

	@property
	def is_online(self) -> bool:
		return self._last_valid_reply + datetime.timedelta(seconds=5) >= datetime.datetime.now()

	def get_next_command_data(self):
		if self.message_control.sequence == 0:
			return PollCommand(self.address)

		if self._use_secure_channel and not self._secure_channel.is_initialized:
			return SecurityInitializationRequestCommand(self.address, self._secure_channel.server_random_number)

		if self._use_secure_channel and not self._secure_channel.is_established:
			return ServerCryptogramCommand(self.address, self._secure_channel.server_cryptogram)

		if self._commands.empty():
			return PollCommand(self.address)
		else:
			command = self._commands.get(False)
			return command

	def send_command(self, command):
		self._commands.put(command)

	def valid_reply_has_been_received(self):
		self.message_control.increment_sequence()
		self._last_valid_reply = datetime.datetime.now()

	def initialize_secure_channel(self, reply):
		reply_data = reply.extract_reply_data
		self._secure_channel.initialize(reply_data[:8], reply_data[8:16], reply_data[16:32])

	def validate_secure_channel_establishment(self, reply) -> bool:
		if not reply.secure_cryptogram_has_been_accepted():
			log.debug("Cryptogram not accepted")
			return False

		self._secure_channel.establish(reply.extract_reply_data)
		return True

	def generate_mac(self, message: bytes, is_command: bool):
		return self._secure_channel.generate_mac(message, is_command)

	def reset_security(self):
		self._secure_channel.reset()

	def encrypt_data(self, data: bytes):
		return self._secure_channel.encrypt_data(data)

	def decrypt_data(self, data: bytes):
		return self._secure_channel.decrypt_data(data)
