from binascii import unhexlify as uhx
from Crypto.Cipher import AES
import os
import serial
import sys
import time
import logging

log_format = "%(asctime)s::%(levelname)s::%(name)s::"\
             "%(filename)s::%(lineno)d::%(message)s"

logging.basicConfig(filename='ps3_cxr_syscon.log', filemode='w', format=log_format, level=logging.DEBUG)

class PS3UART(object):
    ser = serial.Serial()
    type = ''

    sc2tb = uhx('71f03f184c01c5ebc3f6a22a42ba9525')  # Syscon to TestBench Key    (0x130 xor 0x4578)
    tb2sc = uhx('907e730f4d4e0a0b7b75f030eb1d9d36')  # TestBench to Syscon Key    (0x130 xor 0x4588)
    value = uhx('3350BD7820345C29056A223BA220B323')  # 0x45B8
    zero  = uhx('00000000000000000000000000000000')

    auth1r_header = uhx('10100000FFFFFFFF0000000000000000')
    auth2_header  = uhx('10010000000000000000000000000000')

    def aes_decrypt_cbc(self, key, iv, input):
        return AES.new(key, AES.MODE_CBC, iv).decrypt(input)

    def aes_encrypt_cbc(self, key, iv, input):
        return AES.new(key, AES.MODE_CBC, iv).encrypt(input)

    def __init__(self, port, type):
        self.ser.port = port
        if(type == 'CXR'):
            self.ser.baudrate = 57600
        elif(type == 'CXRF'):
            self.ser.baudrate = 115200
        else:
            assert(False)
        self.type = type
        self.ser.timeout = 0.1
        self.ser.open()
        assert(self.ser.isOpen())
        self.ser.flush()

    def __del__(self):
        self.ser.close()

    def send(self, data):
        self.ser.write(data.encode('ascii'))

    def receive(self):
        return self.ser.read(self.ser.inWaiting())

    def command(self, com, wait = 1, verbose = False):
        if(verbose):
            print('Command: ' + com)

        if(self.type == 'CXR'):
            length = len(com)
            checksum = sum(bytearray(com)) % 0x100
            if(length <= 10):
                self.send('C:{:02X}:{}\r\n'.format(checksum, com))
            else:
                j = 10
                self.send('C:{:02X}:{}'.format(checksum, com[0:j]))
                for i in xrange(length - j, 15, -15):
                    self.send(com[j:j+15])
                    j += 15
                self.send(com[j:] + '\r\n')
        else:
            self.send(com + '\r\n')

        time.sleep(wait)
        answer = self.receive().decode('ascii').strip()
        if(verbose):
            print('Answer: ' + answer)

        if(self.type == 'CXR'):
            answer = answer.split(':')
            if(len(answer) != 3):
                return ('Answer length', [])
            checksum = sum(bytearray(answer[2], 'ascii')) % 0x100
            if(answer[0] != 'R' and answer[0] != 'E'):
                return ('Magic', [])
            if(answer[1] != hex(checksum)[2:].upper()):
                return ('Checksum', [])
            data = answer[2].split(' ')
            if(answer[0] == 'R' and len(data) < 2 or answer[0] == 'E' and len(data) != 2):
                return ('Data length', [])
            if(data[0] != 'OK' or len(data) < 2):
                return (int(data[1], 16), [])
            else:
                return (int(data[1], 16), data[2:])
        else:
            return (0, [answer])

    def auth(self):
        if(self.type == 'CXR'):
            auth1r = self.command('AUTH1 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
            if(auth1r[0] == 0 and auth1r[1] != []):
                auth1r = uhx(auth1r[1][0])
                if(auth1r[0:0x10] == self.auth1r_header):
                    data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[0x10:0x40])
                    if(data[0x8:0x10] == self.zero[0x0:0x8] and data[0x10:0x20] == self.value and data[0x20:0x30] == self.zero):
                        new_data = data[0x8:0x10] + data[0x0:0x8] + self.zero + self.zero
                        auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                        auth2r = self.command('AUTH2 ' + ''.join('{:02X}'.format(ord(c)) for c in (self.auth2_header + auth2_body)))
                        if(auth2r[0] == 0):
                            return 'Auth successful'
                        else:
                            return 'Auth failed'
                    else:
                        return 'Auth1 response body invalid'
                else:
                    return 'Auth1 response header invalid'
            else:
                return 'Auth1 response invalid'
        else:
            scopen = self.command('scopen')
            if('SC_READY' in scopen[1][0]):
                auth1r = self.command('10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
                auth1r = auth1r[1][0].split('\r')[1][1:]
                if(len(auth1r) == 128):
                    auth1r = uhx(auth1r)
                    if(auth1r[0:0x10] == self.auth1r_header):
                        data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[0x10:0x40])
                        if(data[0x8:0x10] == self.zero[0x0:0x8] and data[0x10:0x20] == self.value and data[0x20:0x30] == self.zero):
                            new_data = data[0x8:0x10] + data[0x0:0x8] + self.zero + self.zero
                            auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                            auth2r = self.command(''.join('{:02X}'.format(ord(c)) for c in (self.auth2_header + auth2_body)))
                            if('SC_SUCCESS' in auth2r[1][0]):
                                return 'Auth successful'
                            else:
                                return 'Auth failed'
                        else:
                            return 'Auth1 response body invalid'
                    else:
                        return 'Auth1 response header invalid'
                else:
                    return 'Auth1 response invalid'
            else:
                return 'scopen response invalid'

def main(argc, argv):
    if(argc < 3):
        print(os.path.basename(__file__) + ' <serial port> <sc type ["CXR", "CXRF"]>')
        sys.exit(1)
    ps3 = PS3UART(argv[1], argv[2])
    while True:
        input = raw_input('>$ ')
        if(input.lower() == 'auth'):
            print(ps3.auth())
            continue
        if(input.lower() == 'exit'):
            break
        ret = ps3.command(input)
        if(argv[2] == 'CXR'):
            if(isinstance(ret[0], (int, long))):
                print('{:08X} '.format(ret[0]) + ' '.join(ret[1]))
            else:
                print(ret[0])
        else:
            print(ret[1][0].decode('ascii'))

        logging.info('input: {}')
        
        logging.info('ret: {}')


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
