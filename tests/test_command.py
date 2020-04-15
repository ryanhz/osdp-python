#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for OSDP Comnands"""

import os
import sys
import unittest
import datetime

sys.path.insert(0, os.path.abspath('..'))
from osdp import *


class CommandTestCase(unittest.TestCase):

	"""Test commands for OSDP Python Module."""

	def setUp(self):
		"""Setup."""

	def tearDown(self):
		"""Teardown."""

	def test_poll_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = PollCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F07000160C6')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_id_report_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)
		self.assertEqual(device.message_control.sequence, 0)

		command = IdReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0800006100C5')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_device_capabilities_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = DeviceCapabilitiesCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0800016200C3')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_input_status_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = InputStatusReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F07000165C1')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_output_status_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		command = OutputStatusReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F07000266BF')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_led_control_command_granted_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

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
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F15000269000002020102000A0000000000009D')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_led_control_command_denied_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

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
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F15000169000002020101000A0000000000009F')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_buzzer_control_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		reader_buzzer_control = ReaderBuzzerControl(
			reader_number = 0x0,
			tone_code = ToneCode.TBD,
			on_time = 0x02,
			off_time = 0x01,
			count = 0x03
		)
		command = ReaderBuzzerControlCommand(address=0x7F, reader_buzzer_control = reader_buzzer_control)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0C00026A0003020103AD')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_text_output_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		reader_text_output = ReaderTextOutput(
			reader_number = 0x0,
			text_command = TextCommand.PermanentTextNoWrap,
			temp_text_time = 0x00,
			row = 0x00,
			column = 0x00,
			text = "test"
		)
		command = ReaderTextOutputCommand(address=0x7F, reader_text_output = reader_text_output)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F1100016B00010000000474657374EC')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_set_date_time_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		timestamp = datetime.datetime(
			year = 2019,
			month = 11,
			day = 12,
			hour = 9,
			minute = 2,
			second = 0
		)
		command = SetDateTimeCommand(address=0x7F, timestamp = timestamp)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0E00036DE3070B0C090200A4')

	def test_reader_mfg_command_checksum(self):
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		manufacturer_data = bytes([0x0B, 0x0E, 0x0E, 0x0F])
		command = ManufacturerSpecificCommand(address=0x7F, manufacturer_data = manufacturer_data)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0B0001800B0E0E0F6C')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_poll_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = PollCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F08000560A5E1')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		command = PollCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F08000760C787')

	def test_id_report_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)
		self.assertEqual(device.message_control.sequence, 0)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		command = IdReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F09000661003F88')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_device_capabilities_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = DeviceCapabilitiesCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F09000562003C84')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_input_status_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		command = InputStatusReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0800066553E4')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_output_status_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		command = OutputStatusReportCommand(address=0x7F)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0800076601E7')

	def test_reader_led_control_command_granted_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

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
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F16000569000002020102000A0000000000009134')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_led_control_command_denied_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

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
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F16000669000002020101000A00000000000098F1')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_buzzer_control_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		reader_buzzer_control = ReaderBuzzerControl(
			reader_number = 0x0,
			tone_code = ToneCode.DefaultTone,
			on_time = 0x02,
			off_time = 0x00,
			count = 0x01
		)
		command = ReaderBuzzerControlCommand(address=0x7F, reader_buzzer_control = reader_buzzer_control)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0D00066A00020200010B7D')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_text_output_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		reader_text_output = ReaderTextOutput(
			reader_number = 0x0,
			text_command = TextCommand.PermanentTextNoWrap,
			temp_text_time = 0x00,
			row = 0x00,
			column = 0x00,
			text = "hello, universe"
		)
		command = ReaderTextOutputCommand(address=0x7F, reader_text_output = reader_text_output)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F1D00076B00010000000F68656C6C6F2C20756E6976657273650370')

	def test_set_date_time_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		timestamp = datetime.datetime(
			year = 2019,
			month = 0x0B,
			day = 0x1D,
			hour = 0x10,
			minute = 0x11,
			second = 0x12
		)
		command = SetDateTimeCommand(address=0x7F, timestamp = timestamp)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0F00056DE3070B1D101112DEFA')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_reader_mfg_command_crc(self):
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		manufacturer_data = bytes([0x0B, 0x0E, 0x0E, 0x0F])
		command = ManufacturerSpecificCommand(address=0x7F, manufacturer_data = manufacturer_data)
		content = command.build_command(device)
		self.assertEqual(content.hex().upper(), '537F0C0007800B0E0E0FEDCC')

if __name__ == '__main__':
	unittest.main()