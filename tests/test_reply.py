#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for OSDP Replies"""

import os
import sys
import unittest
import datetime
from uuid import UUID, uuid4

sys.path.insert(0, os.path.abspath('..'))
from osdp import *


class ReplyTestCase(unittest.TestCase):

	"""Test commands for OSDP Python Module."""

	def setUp(self):
		"""Setup."""

	def tearDown(self):
		"""Teardown."""

	def test_poll_reply_no_data_checksum(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53 FF 07 00 01 40 66')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.Ack)
		self.assertEqual(reply.extract_reply_data, b'')

		message = reply.build_reply(address=0x7F, control=device.message_control).hex().upper()
		self.assertEqual(message, data.hex().upper())

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_poll_reply_card_data_checksum(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53 FF 0F 00 02 50 FF 01 1A 00 CD 22 C7 16 67')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.RawReaderData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF011A00CD22C716')

		card_data = RawCardData.parse_data(reply)
		self.assertEqual(card_data.data.hex().upper(), 'CD22C716')

		message = reply.build_reply(address=0x7F, control=device.message_control).hex().upper()
		self.assertEqual(message, data.hex().upper())

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_poll_reply_key_data_checksum(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=False, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53 FF 0D 00 02 53 FF 04 31 32 33 34 7F')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.KeypadData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF0431323334')

		keypad_data = KeypadData.parse_data(reply)
		self.assertEqual(keypad_data.data.hex().upper(), '31323334')

		message = reply.build_reply(address=0x7F, control=device.message_control).hex().upper()
		self.assertEqual(message, data.hex().upper())

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)


	def test_poll_reply_no_data_crc(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53 FF 08 00 07 40 75 81')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.Ack)
		self.assertEqual(reply.extract_reply_data, b'')

		message = reply.build_reply(address=0x7F, control=device.message_control).hex().upper()
		self.assertEqual(message, data.hex().upper())

	def test_poll_reply_card_data_crc(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53 FF 10 00 05 50 FF 01 1A 00 CD 22 C7 16 00 C9 ')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.RawReaderData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF011A00CD22C716')

		card_data = RawCardData.parse_data(reply)
		self.assertEqual(card_data.data.hex().upper(), 'CD22C716')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

	def test_poll_reply_key_data_crc(self):
		bus_id = uuid4()
		device = Device(address=0x7F, use_crc=True, use_secure_channel=False)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 1)

		command = PollCommand(address=0x7F)
		data = bytes.fromhex('53FF0E000553FF043132333481B6')
		reply = Reply.parse(data, bus_id, command, device)
		self.assertEqual(reply.type, ReplyType.KeypadData)
		self.assertEqual(reply.extract_reply_data.hex().upper(), 'FF0431323334')

		keypad_data = KeypadData.parse_data(reply)
		self.assertEqual(keypad_data.data.hex().upper(), '31323334')

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 2)

		device.message_control.increment_sequence()
		self.assertEqual(device.message_control.sequence, 3)

if __name__ == '__main__':
	unittest.main()