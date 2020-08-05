#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for OSDP Bus"""

import logging
import os
import sys
import time
import unittest

from context import *

log = logging.getLogger('osdp')


class ControlPanelTestCase(unittest.TestCase):

	"""Test Bus for OSDP Python Module."""

	def setUp(self):
		"""Setup."""
		self.last_reply = None

	def tearDown(self):
		"""Teardown."""

	def test_cp_checksum_unsecure(self):
		conn = SerialPortOsdpConnection(port='/dev/tty.wchusbserial1420', baud_rate=9600)
		cp = ControlPanel()
		bus_id = cp.start_connection(conn)
		self.assertIsNotNone(bus_id)

		cp.add_device(connection_id=bus_id, address=0x7F, use_crc=False, use_secure_channel=False)

		id_report = cp.id_report(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(id_report)

		device_capabilities = cp.device_capabilities(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(device_capabilities)

		local_status = cp.local_status(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(local_status)

		input_status = cp.input_status(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(input_status)

		output_status = cp.output_status(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(output_status)

		reader_status = cp.reader_status(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(reader_status)

		output_status = cp.output_status(connection_id=bus_id, address=0x7F)
		print("\r\n")
		print(output_status)

		granted_led = [ReaderLedControl(
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
		result = cp.reader_led_control(connection_id=bus_id, address=0x7F, reader_led_controls=ReaderLedControls(granted_led))
		print("\r\n")
		print(result)

		time.sleep(1.0)

		denied_led = [ReaderLedControl(
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

		result = cp.reader_led_control(connection_id=bus_id, address=0x7F, reader_led_controls=ReaderLedControls(denied_led))
		print("\r\n")
		print(result)

		cp.shutdown()


if __name__ == '__main__':
	unittest.main()
