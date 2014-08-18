import binascii
import StringIO

class PKCS7Encoder():
    """
    Technique for padding a string as defined in RFC 2315, section 10.3,
    note #2
    """
    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""
        pass
 
    def __init__(self, block_size=16):
        if block_size < 1 or block_size > 99:
            raise InvalidBlockSizeError('The block size must be between 1 ' \
                    'and 99')
        self.block_size = block_size
 
    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = binascii.unhexlify('%02x' % amount_to_pad)
        return text + pad * amount_to_pad
 
    def decode(self, text):
        pad = int(binascii.hexlify(text[-1]), 16)
        return text[:-pad]
          
class ZerosEncoder():
    """
    Technique for padding a string as defined in RFC 2315, section 10.3,
    note #2
    """
    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""
        pass
 
    def __init__(self, block_size=16):
        if block_size < 1 or block_size > 99:
            raise InvalidBlockSizeError('The block size must be between 1 ' \
                    'and 99')
        self.block_size = block_size
 
    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = '\x00'
        return text + pad * amount_to_pad
 
    def decode(self, text):
        #print binascii.hexlify(text[-1])
        #pad = int(binascii.hexlify(text[-1]), 16)
        return text.rstrip('\x00')
