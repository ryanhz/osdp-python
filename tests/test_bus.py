#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for OSDP Bus"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
from osdp import *
from .puppet_connection import PuppetOsdpConnection

log = logging.getLogger('osdp')

class BusTestCase(unittest.TestCase):

	"""Test Bus for OSDP Python Module."""

	def setUp(self):
		"""Setup."""
		self.last_reply = None

	def tearDown(self):
		"""Teardown."""

	def test_id_report_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)		

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		connection.should_reply = bytes.fromhex('53 FF 13 00 03 45 A4 D9 A4 03 FF 33 00 01 70 03 00 02 87')

		data = bytearray([Bus.DRIVER_BYTE])
		command = IdReportCommand(address=0x7F)

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.PdIdReport)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'A4D9A403FF33000170030002')

		device_id = DeviceIdentification.parse_data(reply)
		self.assertEqual(device_id.serial_number, 1879113779)

	def test_poll_no_data_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)		

		connection.should_reply = bytes.fromhex('53 FF 07 00 01 40 66')

		data = bytearray([Bus.DRIVER_BYTE])
		command = PollCommand(address=0x7F)

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.Ack)
		self.assertEqual(reply.extract_reply_data, b'')

	def test_poll_card_data_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)		

		connection.should_reply = bytes.fromhex('53 FF 0F 00 02 50 FF 01 1A 00 CD 22 C7 16 67')

		data = bytearray([Bus.DRIVER_BYTE])
		command = PollCommand(address=0x7F)

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.RawReaderData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF011A00CD22C716')

		card_data = RawCardData.parse_data(reply)
		self.assertEqual(card_data.data.hex().upper(), 'CD22C716')

	def test_poll_keypad_data_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)		

		connection.should_reply = bytes.fromhex('53 FF 0D 00 02 53 FF 04 31 32 33 34 7F')

		data = bytearray([Bus.DRIVER_BYTE])
		command = PollCommand(address=0x7F)

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.KeypadData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF0431323334')

		keypad_data = KeypadData.parse_data(reply)
		self.assertEqual(keypad_data.data.hex().upper(), '31323334')

	def test_reader_led_control_granted_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)		

		connection.should_reply = bytes.fromhex('53 FF 07 00 02 40 65')

		data = bytearray([Bus.DRIVER_BYTE])
		reader_led_controls = [ReaderLedControl(
			reader_number = 0x0,
			led_number = 0x0,
			temporary_mode = TemporaryReaderControlCode.SetTemporaryAndStartTimer,
			temporary_on_time = 0x02,
			temporary_off_time = 0x01,
			temporary_on_color = LedColor.Green,
			temporary_off_color = LedColor.Black,
			temporary_timer = 0x000A,
			permanent_mode = PermanentReaderControlCode.Nop,
			permanent_on_time = 0x00,
			permanent_off_time = 0x00,
			permanent_on_color = LedColor.Black,
			permanent_off_color = LedColor.Black
		)]
		command = ReaderLedControlCommand(address=0x7F, reader_led_controls = ReaderLedControls(reader_led_controls))

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.Ack)
		self.assertEqual(reply.extract_reply_data, b'')

	def test_reader_led_control_denied_checksum(self):
		connection = PuppetOsdpConnection()
		connection.open()

		bus = Bus(connection=connection, on_reply_received=None)
		device = bus.add_device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)		

		connection.should_reply = bytes.fromhex('53 FF 07 00 01 40 66')

		data = bytearray([Bus.DRIVER_BYTE])
		reader_led_controls = [ReaderLedControl(
			reader_number = 0x0,
			led_number = 0x0,
			temporary_mode = TemporaryReaderControlCode.SetTemporaryAndStartTimer,
			temporary_on_time = 0x02,
			temporary_off_time = 0x01,
			temporary_on_color = LedColor.Red,
			temporary_off_color = LedColor.Black,
			temporary_timer = 0x000A,
			permanent_mode = PermanentReaderControlCode.Nop,
			permanent_on_time = 0x00,
			permanent_off_time = 0x00,
			permanent_on_color = LedColor.Black,
			permanent_off_color = LedColor.Black
		)]
		command = ReaderLedControlCommand(address=0x7F, reader_led_controls = ReaderLedControls(reader_led_controls))

		reply = bus.send_command_and_receive_reply(data, command, device)
		self.assertIsNotNone(reply)
		self.assertEqual(reply.type, ReplyType.Ack)
		self.assertEqual(reply.extract_reply_data, b'')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

if __name__ == '__main__':
	unittest.main()