===========
OSDP Python
===========

OSDP Python is a python framework implementation of the Open Supervised Device Protocol (OSDP). This protocol has been adopted by the Security Industry Association(SIA) to standardize communication to access control hardware. Further information can be found at  `http://www.osdp-connect.com <http://www.osdp-connect.com>`_.

This project is highly inspired by @bytedreamer's `OSDP.Net <https://github.com/bytedreamer/OSDP.Net>`


License
-------
 - Apache

Quick Start
-----------

Installation
------------

To install OSDP, use `pip <https://pip.pypa.io/en/stable/quickstart/>`_ or `pipenv <https://docs.pipenv.org/en/latest/>`_:

.. code-block:: console

    $ pip install -U osdp

This module depends on

 - pycryptodome
 - pyserial


Example Usage
~~~~~~~~~~~~~

.. code-block:: python

    >>> from osdp import *
    >>> conn = SerialPortOsdpConnection(port='/dev/tty.wchusbserial1420', baud_rate=9600)
    >>> cp = ControlPanel()
    >>> bus_id = cp.start_connection(conn)
    >>> cp.add_device(connection_id=bus_id, address=0x7F, use_crc=True, use_secure_channel=False)
    >>> id_report = cp.id_report(connection_id=bus_id, address=0x7F)
    >>> device_capabilities = cp.device_capabilities(connection_id=bus_id, address=0x7F)
    >>> local_status = cp.local_status(connection_id=bus_id, address=0x7F)
    >>> input_status = cp.input_status(connection_id=bus_id, address=0x7F)
    >>> output_status = cp.output_status(connection_id=bus_id, address=0x7F)
    >>> cp.shutdown()

