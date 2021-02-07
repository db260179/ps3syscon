if(len(sys.argv) < 3):
    print os.path.basename(__file__) + ' <serial port> <output file>'
    sys.exit(1)
 
ps3 = PS3UART(sys.argv[1], 'CXR')
print "Version: " + ps3.command("VER")[1][0]
print ps3.auth()
f = open(sys.argv[2], 'wb')
block_size = 0x40
print "Dumping NVS"
failed = []
for i in xrange(0x2C00, 0x7400, block_size): # 0x7400 for CXR713, 0x4400 for CXR714
    print "Reading 0x{:04X}".format(i)
    data = ps3.command("R8 {:08X} {:02X}".format(i, block_size))
    ret = data[0]
    if ret == 0:
        f.write((data[1][0]).decode('hex'))
    else:
        print "Failed: " + str(ret)
        failed += [i]
        f.write(("A"*block_size*2).decode('hex'))
     
f.close()
time.sleep(2)
print "\nRetrying failed offsets"
for i in failed:
    print "Reading 0x{:04X}".format(i)
    for j in xrange(0, block_size, block_size/4):
        while True:
            data = ps3.command("R8 {:08X} {:02X}".format(i+j, block_size/4))
            ret = data[0]
            if ret == 0:
                print data[1][0]
                break
            time.sleep(2)
