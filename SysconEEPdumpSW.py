if(len(sys.argv) < 3):
    print(os.path.basename(__file__) + ' <serial port> <output file>')
    sys.exit(1)
  
ps3 = PS3UART(sys.argv[1], 'SW')
print('Version: ' + ps3.command('VER')[1][0])
print(ps3.auth())
f = open(sys.argv[2], 'wb')
block_size = 0x40
print('Dumping NVS')
for i in range(0x0, 0x1400, block_size):
    print('Reading 0x{:04X}'.format(i))
    data = ps3.command('EEP GET {:08X} {:02X}'.format(i, block_size))
    ret = data[0]
    temp = ''
    if ret == 0:
        for i in range(2, len(data[1])):
            temp += data[1][i][2:-2].replace(' ', '')
        f.write(bytearray.fromhex(temp))
    else:
        print('Failed: ' + str(ret))
      
f.close()
