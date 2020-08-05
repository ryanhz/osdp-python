import logging
from datetime import datetime, timedelta
import time
from threading import Lock
from uuid import uuid4

from ._types import ReplyType, ErrorCode
from ._connection import OsdpConnection
from ._device import Device
from ._message import Message
from ._command import Command
from ._reply import Reply

log = logging.getLogger('osdp')


class Bus:
	'''
	A group of OSDP devices sharing communications
	'''
	DRIVER_BYTE = 0xFF

	def __init__(self, connection: OsdpConnection, on_reply_received):
		self._connection = connection
		self._on_reply_received = on_reply_received
		self._configured_devices = {}
		self._configured_devices_lock = Lock()
		self._read_timeout = timedelta(milliseconds=200)
		self.id = uuid4()
		self._is_shutting_down = False

	@property
	def idle_line_delay(self) -> timedelta:
		return timedelta(milliseconds=(1000.0 / self._connection.baud_rate * 16.0) * 100)

	def close(self):
		self._is_shutting_down = True
		self._connection.close()

	def send_command(self, command: Command):
		found_device = self._configured_devices.get(command.address)
		if found_device is not None:
			found_device.send_command(command)
		else:
			log.warning("Device not found with address %s", command.address)

	def add_device(self, address: int, use_crc: bool, use_secure_channel: bool) -> Device:
		found_device = self._configured_devices.get(address)
		self._configured_devices_lock.acquire()
		if found_device is not None:
			self._configured_devices.pop(address)
		self._configured_devices[address] = Device(address, use_crc, use_secure_channel)
		self._configured_devices_lock.release()
		return self._configured_devices[address]

	def remove_device(self, address: int):
		found_device = self._configured_devices.get(address)
		self._configured_devices_lock.acquire()
		if found_device is not None:
			self._configured_devices.pop(address)
		self._configured_devices_lock.release()
		return found_device

	def is_online(self, address: int) -> bool:
		found_device = self._configured_devices.get(address)
		if found_device is None:
			return False
		else:
			return found_device.is_online

	def run_polling_loop(self):
		last_message_sent_time = datetime.min
		while not self._is_shutting_down:
			if not self._connection.is_open:
				try:
					self._connection.open()
				except:
					log.exception("Error while opening connection %s", self._connection)

			time_difference = timedelta(milliseconds=100) - (datetime.now() - last_message_sent_time)
			time.sleep(max(time_difference, timedelta(seconds=0)).total_seconds())

			if not self._configured_devices:
				last_message_sent_time = datetime.now()
				continue

			for device in list(self._configured_devices.values()):
				data = bytearray([self.DRIVER_BYTE])
				command = device.get_next_command_data()

				last_message_sent_time = datetime.now()

				reply = None
				try:
					reply = self.send_command_and_receive_reply(data, command, device)
				except:
					log.exception("Error while sending command %s and receiving reply", command)
					self._connection.close()
					continue

				try:
					self.process_reply(reply, device)
				except:
					log.exception("Error while processing reply %s", reply)
					self._connection.close()
					continue

				time.sleep(self.idle_line_delay.total_seconds())

	def process_reply(self, reply: Reply, device: Device):
		if not reply.is_valid_reply:
			return

		if reply.is_secure_message:
			mac = device.generate_mac(reply.message_for_mac_generation, False)
			if not reply.is_valid_mac(mac):
				device.reset_security()
				return

		if reply.type != ReplyType.Busy:
			device.valid_reply_has_been_received()

		if reply.type == ReplyType.Nak:
			extract_reply_data = reply.extract_reply_data
			error_code = ErrorCode(extract_reply_data[0])
			if error_code == ErrorCode.DoesNotSupportSecurityBlock or error_code == ErrorCode.DoesNotSupportSecurityBlock:
				device.reset_security()

		if reply.type == ReplyType.CrypticData:
			device.initialize_secure_channel(reply)
		elif reply.type == ReplyType.InitialRMac:
			if device.validate_secure_channel_establishment(reply):
				log.debug("Secure session established.")

		if self._on_reply_received is not None:
			self._on_reply_received(reply)

	def send_command_and_receive_reply(self, data: bytearray, command: Command, device: Device) -> Reply:
		command_data = None
		try:
			command_data = command.build_command(device)
		except:
			log.exception("Error while building command %s", command)
			raise
		data.extend(command_data)

		log.debug("Raw command data: %s", command_data.hex())

		self._connection.write(bytes(data))

		reply_buffer = bytearray()

		if not self.wait_for_start_of_message(reply_buffer):
			raise TimeoutError("Timeout waiting for reply message")

		if not self.wait_for_message_length(reply_buffer):
			raise TimeoutError("Timeout waiting for reply message length")

		if not self.wait_for_rest_of_message(reply_buffer, self.extract_message_length(reply_buffer)):
			raise TimeoutError("Timeout waiting for rest of reply message")

		log.debug("Raw reply data: %s", reply_buffer.hex())

		return Reply.parse(bytes(reply_buffer), self.id, command, device)

	def extract_message_length(self, reply_buffer: bytearray) -> int:
		return int.from_bytes(bytes(reply_buffer[2:3]), byteorder='little')

	def wait_for_rest_of_message(self, buffer: bytearray, reply_length: int):
		while len(buffer) < reply_length:
			bytes_read = self._connection.read(reply_length - len(buffer))
			if len(bytes_read) > 0:
				buffer.extend(bytes_read)
			else:
				return False
		return True

	def wait_for_message_length(self, buffer: bytearray) -> bool:
		while len(buffer) < 4:
			bytes_read = self._connection.read(4)
			if len(bytes_read) > 0:
				buffer.extend(bytes_read)
			else:
				return False
		return True

	def wait_for_start_of_message(self, buffer: bytearray) -> bool:
		while True:
			bytes_read = self._connection.read(1)
			if len(bytes_read) == 0:
				return False

			if bytes_read[0] != Message.SOM:
				continue

			buffer.extend(bytes_read)
			break
		return True
