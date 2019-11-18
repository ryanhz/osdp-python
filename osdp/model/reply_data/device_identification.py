

class DeviceIdentification:

	def __init__(self, vendor_code: bytes, model_number: int, version: int, serial_number: int, firmware_major: int, firmware_minor: int, firmware_build: int):
		self.vendor_code = vendor_code
		self.model_number = model_number
		self.version = version
		self.serial_number = serial_number
		self.firmware_major = firmware_major
		self.firmware_minor = firmware_minor
		self.firmware_build = firmware_build

	@staticmethod
	def parse_data(reply: Reply) -> DeviceIdentification:
		data = reply.extract_reply_data
		if len(data)!=12:
			raise ValueError("Invalid size for the data")

		vendor_code = data[0:3]
		model_number = data[3]
		version = data[4]
		serial_number = Message.convert_bytes_to_int(data[5:9])
		firmware_major = data[9]
		firmware_minor = data[10]
		firmware_build = data[11]
		return DeviceIdentification(vendor_code, model_number, version, serial_number, firmware_major, firmware_minor, firmware_build)

	def __repr__(self):
		return "     Vendor Code: {0}\n    Model Number: {1}\n         Version: {2}\n   Serial Number: {3}\nFirmware Version: {4}.{5}.{6}".format(
			self.vendor_code.hex(), self.model_number, self.version, Message.convert_int_to_bytes(self.serial_number).hex(), self.firmware_major, self.firmware_minor, self.firmware_build)


