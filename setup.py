from distutils.core import setup

setup(
	name = 'osdp',
	packages = ['osdp'],
	version = '1.3',
	license='apache-2.0',
	description = 'A Python control panel implementation of the Open Supervised Device Protocol (OSDP)',
	long_description = open('README.rst').read(),
	author = 'Ryan Hu',
	author_email = 'huzhiren@gmail.com',
	url = 'https://github.com/ryanhz/osdp-python',
	download_url = 'https://github.com/ryanhz/osdp-python/archive/v1.3.tar.gz',
	keywords = ['OSDP', 'Open Supervised Device Protocol', 'Access Control'],
	install_requires=[
		'pycryptodome',
		'pyserial >= 3.4',
	],
	classifiers=[
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Topic :: Communications',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
	],
)