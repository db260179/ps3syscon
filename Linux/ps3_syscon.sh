#!/bin/bash

if [ "${DEBUG}" = "true" ]; then
  set -ex
else
  set -e
fi

ps3_syscon_uart()
{
    port=$2
    mode=$3

    if [ "${port}" = "" ]; then
      echo "Please specify the serial port to use i.e. /dev/ttyUSB0"
    
      serialPortList=$(ls /dev/ | grep ttyUSB*)
      for s in $serialPortList
      do echo "$s is connected!"
      done

      exit 1
    fi

    if [ "${mode}" = "" ]; then
      echo "Please specify the mode to use i.e. Mullion - CXR = External mode, CXRF = Internal mode"
      echo "Sherwood = SW"
      exit 1
    fi

    ./ps3_syscon_uart_script.py ${port} ${mode}

}

syscon_dump_cxr()
{
    port=$2
    outputfile=$3

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
    port=$2
    outputfile=$3

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
    port=$2
    outputfile=$3

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
    port=$2
    patchfile=$3

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



case "$1" in
  syscon)
    ps3_syscon_uart
    ;;
  dump-cxr)
    syscon_dump_cxr
    ;;
  dump-cxrf)
    syscon_dump_cxrf
    ;;
  dump-sw)
    syscon_dump_sw
    ;;
  patch-cxr)
    syscon_patch_cxr
    ;;
  *)
    echo ""
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
