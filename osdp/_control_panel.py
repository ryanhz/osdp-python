import logging
from uuid import UUID
from threading import Thread

from ._types import (
	DeviceIdentification, DeviceCapabilities, LocalStatus, InputStatus, OutputStatus, ReaderStatus,
	OutputControls, ReplyType, ReaderLedControls, DataEvent, Nak, RawCardData, KeypadData
)
from ._connection import OsdpConnection
from ._command import (
	Command, IdReportCommand, DeviceCapabilitiesCommand, LocalStatusReportCommand, InputStatusReportCommand,
	OutputStatusReportCommand, ReaderStatusReportCommand, OutputControlCommand, ReaderLedControlCommand,
	KeySetCommand
)
from ._reply import Reply
from ._bus import Bus


log = logging.getLogger('osdp')
console_handler = logging.StreamHandler()
log.addHandler(console_handler)


class ControlPanel:

	def __init__(self):
		self._buses = {}
		self._reply_handlers = []
		self._reply_timeout = 5.0

	def start_connection(self, connection: OsdpConnection) -> UUID:
		bus = Bus(connection, self.on_reply_received)
		self._buses[bus.id] = bus
		thread = Thread(target=bus.run_polling_loop)
		thread.start()
		return bus.id

	def send_custom_command(self, connection_id: UUID, command: Command):
		self.send_command(connection_id, command)

	def id_report(self, connection_id: UUID, address: int) -> DeviceIdentification:
		return DeviceIdentification.parse_data(self.send_command(connection_id, IdReportCommand(address)))

	def device_capabilities(self, connection_id: UUID, address: int) -> DeviceCapabilities:
		return DeviceCapabilities.parse_data(self.send_command(connection_id, DeviceCapabilitiesCommand(address)))

	def local_status(self, connection_id: UUID, address: int) -> LocalStatus:
		return LocalStatus.parse_data(self.send_command(connection_id, LocalStatusReportCommand(address)))

	def input_status(self, connection_id: UUID, address: int) -> InputStatus:
		return InputStatus.parse_data(self.send_command(connection_id, InputStatusReportCommand(address)))

	def output_status(self, connection_id: UUID, address: int) -> OutputStatus:
		return OutputStatus.parse_data(self.send_command(connection_id, OutputStatusReportCommand(address)))

	def reader_status(self, connection_id: UUID, address: int) -> ReaderStatus:
		return ReaderStatus.parse_data(self.send_command(connection_id, ReaderStatusReportCommand(address)))

	def output_control(self, connection_id: UUID, address: int, output_controls: OutputControls) -> bool:
		reply = self.send_command(connection_id, OutputControlCommand(address, output_controls))
		return reply.type == ReplyType.Ack or reply.type == ReplyType.OutputStatusReport

	def reader_led_control(self, connection_id: UUID, address: int, reader_led_controls: ReaderLedControls) -> bool:
		reply = self.send_command(connection_id, ReaderLedControlCommand(address, reader_led_controls))
		return reply.type == ReplyType.Ack

	def keyset(self, connection_id: UUID, address: int) -> bool:
		reply = self.send_command(connection_id, KeySetCommand(address, bytes([])))
		return reply.type == ReplyType.Ack

	def is_online(self, connection_id: UUID, address: int) -> bool:
		bus = self._buses.get(connection_id)
		if bus is None:
			return False
		else:
			return bus.is_online(address)

	def send_command(self, connection_id: UUID, command: Command) -> Reply:
		event = DataEvent()

		def reply_fetcher(reply: Reply):
			if reply.match_issuing_command(command):
				self._reply_handlers.remove(reply_fetcher)
				event.set_data(reply)

		self._reply_handlers.append(reply_fetcher)
		bus = self._buses[connection_id]
		bus.send_command(command)
		result = event.wait_data(self._reply_timeout)
		if event.is_set():
			return result
		else:
			self._reply_handlers.remove(reply_fetcher)
			raise TimeoutError()

	def shutdown(self):
		for bus in list(self._buses.values()):
			bus.close()

	def add_device(self, connection_id: UUID, address: int, use_crc: bool, use_secure_channel: bool):
		bus = self._buses.get(connection_id)
		if bus is not None:
			bus.add_device(address, use_crc, use_secure_channel)

	def remove_device(self, connection_id: UUID, address: int):
		bus = self._buses.get(connection_id)
		if bus is not None:
			bus.remove_device(address)

	def on_reply_received(self, reply: Reply):
		for reply_hander in self._reply_handlers:
			reply_hander(reply)

		if reply.type == ReplyType.Nak:
			self.on_nak_reply_received(reply.address, Nak.parse_data(reply))

		elif reply.type == ReplyType.LocalStatusReport:
			self.on_local_status_report_reply_received(reply.address, LocalStatus.parse_data(reply))

		elif reply.type == ReplyType.InputStatusReport:
			self.on_input_status_report_reply_received(reply.address, InputStatus.parse_data(reply))

		elif reply.type == ReplyType.OutputStatusReport:
			self.on_output_status_report_reply_received(reply.address, OutputStatus.parse_data(reply))

		elif reply.type == ReplyType.ReaderStatusReport:
			self.on_reader_status_report_reply_received(reply.address, ReaderStatus.parse_data(reply))

		elif reply.type == ReplyType.FormattedReaderData:
			self.on_formatted_reader_data_reply_received(reply.address, reply.extract_reply_data)

		elif reply.type == ReplyType.RawReaderData:
			self.on_raw_card_data_reply_received(reply.address, RawCardData.parse_data(reply))

		elif reply.type == ReplyType.KeypadData:
			self.on_keypad_data_reply_received(reply.address, KeypadData.parse_data(reply))

	def on_nak_reply_received(self, address: int, nak: Nak):
		log.debug("%s < Nak received %s", address, nak)

	def on_local_status_report_reply_received(self, address: int, local_status: LocalStatus):
		log.debug("%s < Local status received %s", address, local_status)

	def on_input_status_report_reply_received(self, address: int, input_status: InputStatus):
		log.debug("%s < Input status received %s", address, input_status)

	def on_output_status_report_reply_received(self, address: int, output_status: OutputStatus):
		log.debug("%s < Output status received %s", address, output_status)

	def on_reader_status_report_reply_received(self, address: int, reader_status: ReaderStatus):
		log.debug("%s < Reader status received %s", address, reader_status)

	def on_formatted_reader_data_reply_received(self, address: int, formatted_reader_data: bytes):
		log.debug("%s < Formatted reader data received %s", address, formatted_reader_data)

	def on_raw_card_data_reply_received(self, address: int, raw_card_data: RawCardData):
		log.debug("%s < Raw reader data received %s", address, raw_card_data)

	def on_keypad_data_reply_received(self, address: int, keypad_data: KeypadData):
		log.debug("%s < Keypad data received %s", address, keypad_data)
