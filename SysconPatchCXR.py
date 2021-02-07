if(len(sys.argv) < 3):
    print os.path.basename(__file__) + ' <serial port> <patch file>'
    sys.exit(1)
 
ps3 = PS3UART(sys.argv[1], 'CXR')
f = open(sys.argv[2], 'rb')
patch = f.read()
f.close()
print "Version: " + ps3.command("VER")[1][0]
print ps3.auth()
patch_area_1 = 0x2800
patch_area_2 = 0x4400 # 0x7400 for CXR713, 0x4400 for CXR714
block_size = 0x40
print "First region"
for i in xrange(0, 0x400, block_size):
    print hex(ps3.command("EEP SET " + hex(i+patch_area_1)[2:] + " " + hex(block_size)[2:] + " " + patch[i:i+block_size].encode('hex'))[0])
 
print "" 
print "Second region"
for i in xrange(0x400, 0x1000, block_size):
    print hex(ps3.command("EEP SET " + hex(i+patch_area_2-0x400)[2:] + " " + hex(block_size)[2:] + " " + patch[i:i+block_size].encode('hex'))[0])
