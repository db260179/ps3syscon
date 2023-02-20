#!/bin/bash
# Syscon helper script for the python scripts

if [ "${DEBUG}" = "true" ]; then
  set -ex
else
  set -e
fi

ps3_syscon_uart()
{
    port="$2"
    mode="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${mode}" = "" ]; then
      echo "Please specify the mode to use i.e. Mullion - CXR = External mode, CXRF = Internal mode Sherwood = SW"
      exit 1
    fi

    echo "If 'auth' is failing, then run the script - ./ps3_diag_serial.py to verify that the serial connection is good!"
    echo "REMEMBER! CXRF needs the DIAG lead to be shorted to GND (not required on SW models)"

    sleep 3

    ./ps3_syscon_uart_script.py ${port} ${mode}

}

syscon_dump_cxr()
{
    port="$2"
    outputfile="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${outputfile}" = "" ]; then
      echo "Please specify the dumped syscon file for CXR i.e. sysconCXR.dump"
      exit 1
    fi

    ./SysconEEPdumpCXR-EXT.py ${port} ${outputfile}
}

syscon_dump_cxrf()
{
    port="$2"
    outputfile="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${outputfile}" = "" ]; then
      echo "Please specify the dumped syscon file for CXRF i.e. sysconCXRF.dump"
      exit 1
    fi

    ./SysconEEPdumpCXRF-INT.py ${port} ${outputfile}
}

syscon_dump_sw()
{
    port="$2"
    outputfile="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${outputfile}" = "" ]; then
      echo "Please specify the dumped syscon file for SW i.e. sysconSW.dump"
      exit 1
    fi

    ./SysconEEPdumpSW.py ${port} ${outputfile}
}

syscon_patch_cxr()
{
    port="$2"
    patchfile="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${patchfile}" = "" ]; then
      echo "Please specify the patch file in CXR mode"
      exit 1
    fi

    ./SysconPatchCXR.py ${port} ${patchfile}
}

ps3_syscon_uart-test()
{
    port="$2"
    baudrate="$3"

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"

      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${baudrate}" = "" ]; then
      echo "Please specify the serial baud rate mode to use i.e. Mullion - 57600 = CXR/SW, 115200 = CXRF"
      exit 1
    fi

    echo "Displaying the serial output - to exit hit the CTRL+C keys"
    echo "Output of session is stored in - ~/ps3_syscon_uart-test.log"
    echo "If screen output is garbage then try swapping the TX and RX leads when powering on the PS3"
    echo "REMEMBER! CXRF needs the DIAG lead to be shorted to GND (not required on SW models)"
    sleep 3
    ./ps3_diag_serial.py -l ~/ps3_syscon_uart-test.log ${port} ${baudrate}

}

sysconhelp()
{
cat <<'EOF'
Example of using the syscon option when first attempt to enter INT mode from EXT mode:
   
Enter syscon EXT mode - $0 syscon /dev/ttyUSB0 CXR
   
In python shell authorise first - $ auth
(If it fails validate that the connections are correct and your serial lead is working - you can rerun this script - ./ps3_syscon.sh syscontest, and check for serial connection issue!)
(CXR should be 'OK' when turning on, CXRF should be '[mullion]' prompt - any other garbage means a bad connection or wrong way TX, RX connections? )
   
If auth was successful will show:
$ Auth successful
   
Set the mode to internal mode:
$ EEP SET 3961 01 00 (Must be in caps on linux systems)
Validate change:
$ EEP GET 3961 01
00000000 00
   
Turn off PS3 motherboard
  
Now ground the DIAG lead if applicable - not required for Sherwood boards
  
Exit out of the python shell - CTRL+C or type 'exit'
  
Turn on PS3 board
   
Enter syscon INT mode - $0 syscon /dev/ttyUSB0 CXRF
In python shell authorise first - $ auth
   
Correct the checksum of the syscon:
   
$ eepcsum
Addr:0x000032fe should be 0x528c
Addr:0x000034fe should be 0x7115
sum:0x0100
Addr:0x000039fe should be 0x0038
Addr:0x00003dfe should be 0x00ff
Addr:0x00003ffe should be 0x00ff
   
Addr:0x000039fe is incorrect so fix it
  
$ w 39FE 38 00 (little endian have the byte swapped)
   
Validate its correct now:
   
$ eepcsum
Addr:0x000032fe should be 0x528c
Addr:0x000034fe should be 0x7115
Addr:0x000039fe should be 0x0038
Addr:0x00003dfe should be 0x00ff
Addr:0x00003ffe should be 0x00ff
  
From now on you can be internal mode CXRF and do commands like - 'errlog and lasterrlog'

Checkout the Fantables docs to tweak your ps3 fan settings in the syscon!

EOF
   
}

case "$1" in
  syscon)
    ps3_syscon_uart "$1" "$2" "$3"
    ;;
  sysconhelp)
    sysconhelp
    ;;
  syscontest)
    ps3_syscon_uart-test "$1" "$2" "$3"
    ;;
  dump-cxr)
    syscon_dump_cxr "$1" "$2" "$3"
    ;;
  dump-cxrf)
    syscon_dump_cxrf "$1" "$2" "$3"
    ;;
  dump-sw)
    syscon_dump_sw "$1" "$2" "$3"
    ;;
  patch-cxr)
    syscon_patch_cxr "$1" "$2" "$3"
    ;;
  *)
    echo ""
    echo "Usage: $0 sysconhelp - Show examples of using the syscon i.e Setting INT mode on first time etc"
    echo "Usage: $0 syscontest - Test serial output port - port = i.e. /dev/ttyUSB0, baudrate = 57600 (CXR) or 115200 (CXRF/SW)"
    echo "Usage: $0 syscon {port} {mode} - port = serial port i.e. /dev/ttyUSB0, mode = CXR (EXT mode) or CXRF (INT mode) or SW"
    echo "Usage: $0 dump-cxr {port} {outputfile} - port = serial port i.e. /dev/ttyUSB0, outputfile = sysconCXR.dump"
    echo "Usage: $0 dump-cxrf {port} {outputfile} - port = serial port i.e. /dev/ttyUSB0, outputfile = sysconCXRF.dump"
    echo "Usage: $0 dump-sw {port} {outputfile} - port = serial port i.e. /dev/ttyUSB0, outputfile = sysconSW.dump"
    echo "Usage: $0 patch-cxr {port} {patchfile} - port = serial port i.e. /dev/ttyUSB0, patchfile = yourpatchfile.patch"
    echo ""
    exit 1
    ;;
esac
shift
