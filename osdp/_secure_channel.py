
from Crypto import Random
from Crypto.Cipher import AES


class SecureChannel:

	default_secure_channel_key = bytes([
		0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
		0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F
	])

	def __init__(self):
		self._cmac = None
		self._enc = None
		self._rmac = None
		self._smac1 = None
		self._smac2 = None

		self.server_random_number = None
		self.server_cryptogram = None
		self.is_initialized = False
		self.is_established = False
		self.reset()

	def initialize(self, cuid: bytes, client_random_number: bytes, client_cryptogram: bytes):
		self._enc = self.generate_key(
			bytes([
				0x01, 0x82,
				self.server_random_number[0], self.server_random_number[1], self.server_random_number[2],
				self.server_random_number[3], self.server_random_number[4], self.server_random_number[5]
			]),
			bytes([0x00] * 8),
			self.default_secure_channel_key
		)

		if client_cryptogram != self.generate_key(self.server_random_number, client_random_number, self._enc):
			raise Exception("Invalid client cryptogram")

		self._smac1 = self.generate_key(
			bytes([
				0x01, 0x01,
				self.server_random_number[0], self.server_random_number[1], self.server_random_number[2],
				self.server_random_number[3], self.server_random_number[4], self.server_random_number[5]
			]),
			bytes([0x00] * 8),
			self.default_secure_channel_key
		)
		self._smac2 = self.generate_key(
			bytes([
				0x01, 0x02,
				self.server_random_number[0], self.server_random_number[1],
				self.server_random_number[2], self.server_random_number[3],
				self.server_random_number[4], self.server_random_number[5]
			]),
			bytes([0x00] * 8),
			self.default_secure_channel_key
		)
		self.server_cryptogram = self.generate_key(
			client_random_number,
			self.server_random_number,
			self._enc
		)
		self.is_initialized = True

	def establish(self, rmac: bytes):
		self._rmac = rmac
		self.is_established = True

	def generate_mac(self, message: bytes, is_command: bool):
		crypto_length = 16
		padding_start = 0x80

		mac = b'\x00' * crypto_length
		current_location = 0
		key = self._smac1
		iv = self._rmac if is_command else self._cmac

		while current_location < len(message):
			input_buffer = bytearray(message[current_location:(current_location + crypto_length)])
			if len(input_buffer) < crypto_length:
				input_buffer.extend(b'\x00' * (crypto_length - len(input_buffer)))

			current_location += crypto_length
			if current_location > len(message):
				key = self._smac2
				if len(message) % crypto_length != 0:
					input_buffer[len(message) % crypto_length] = padding_start

			cipher = AES.new(key, AES.MODE_CBC, iv)
			mac = cipher.encrypt(bytes(input_buffer))
			iv = mac

		if is_command:
			self._cmac = mac
		else:
			self._rmac = mac
		return mac

	def decrypt_data(self, data: bytes) -> bytes:
		padding_start = 0x80

		key = self._enc
		iv = bytes([(~b) & 0xFF for b in self._cmac])
		cipher = AES.new(key, AES.MODE_CBC, iv)
		padded_data = cipher.decrypt(data)
		decrypted_data = bytearray(padded_data)
		while len(decrypted_data) > 0 and decrypted_data[-1] != padding_start:
			decrypted_data.pop()
		if len(decrypted_data) > 0 and decrypted_data[-1] == padding_start:
			decrypted_data.pop()
		return bytes(decrypted_data)

	def encrypt_data(self, data: bytes) -> bytes:
		crypto_length = 16
		padding_start = 0x80
		padded_data = bytearray(data)
		padded_data.append(padding_start)
		while len(padded_data) % crypto_length != 0:
			padded_data.append(0x00)

		key = self._enc
		iv = bytes([(~b) & 0xFF for b in self._rmac])
		cipher = AES.new(key, AES.MODE_CBC, iv)
		return cipher.encrypt(padded_data)

	def reset(self):
		self.server_random_number = Random.new().read(8)
		self.is_initialized = False
		self.is_established = False

	def generate_key(self, first: bytes, second: bytes, key: bytes) -> bytes:
		cipher = AES.new(key, AES.MODE_ECB)
		return cipher.encrypt(first + second)
