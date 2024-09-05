import struct
import logging
from modem.const import CRC16_MAP,CRC32_MAP
from collections.abc import Iterable


# Configure logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG
)

log = logging.getLogger('modem')


def crc16(data, crc=0):
    '''
    Calculates the (unsigned) 16 bit cyclic redundancy check of a byte
    sequence::

        >>> crc = crc16('Hello ')
        >>> crc = crc16('world!', crc)
        >>> print hex(crc)
        0x39db

    '''
    def calc(byte, crc=0):
        if isinstance(byte, bytes):
            b = struct.unpack('B', byte)
        else:
            b = int(byte)

        crc = (crc << 8) ^ CRC16_MAP[((crc >> 8) ^ b) & 0xff]
        return crc

    if isinstance(data, Iterable):
        for byte in data:
            crc = calc(byte, crc)
    else:
        crc = calc(data, crc)
    return crc & 0xffff


def crc32(data, crc=0):
    '''
    Calculates the (unsigned) 32 bit cyclic redundancy check of a byte
    sequence::

        >>> crc = crc32('Hello ')
        >>> crc = crc32('world!', crc)
        >>> print hex(crc)
        0x1b851995

    '''
    def calc(byte, crc=0):
        if isinstance(byte, bytes):
            b = struct.unpack('B', byte)
        else:
            b = int(byte)

        crc = crc ^ 0xffffffff
        crc = (CRC32_MAP[(crc ^ b) & 0xff] ^ (crc >> 8)) ^ 0xffffffff
        return crc

    if isinstance(data, Iterable):
        for byte in data:
            crc = calc(byte, crc)
    else:
        crc = calc(data, crc)
    return crc & 0xffffffff
