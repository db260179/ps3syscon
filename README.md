# ps3syscon
PS3 syscon guide and fault finding

## Linux users  
Required Python 2 or Python 3 - [Linux/ps3_syscon_uart_script.py](/Linux/ps3_syscon_uart_script.py)

## Windows users 
  - [Windows/SysconReader/readme.md](/Windows/SysconReader/readme.md)
  - [Windows/syscon.ps1](Windows/syscon.ps1) (PowerShell script)
    - Tested on Windows PowerShell 5.1 and PowerShell Core 7.2
    - Same syntax as the Python script
    - **Sherwood syscons not guaranteed to be working**

## Any OS (python3-tk)

Python GUI version of the uart script [gui_ps3_syscon_uart_script.py](/gui_ps3_syscon_uart_script.py)

Debian/Ubuntu:

```
sudo apt-get install python3-tk

This command installs the python3-tk package, which includes tkinter for Python 3.
```

Windows: 

tkinter is usually included with the standard Python installation. However, if it's not already installed, you can follow these steps to install it:

```
Open a web browser and go to the official Python website: https://www.python.org/

Click on the "Downloads" tab and scroll down to find the latest stable version of Python 3 for Windows.

Download the installer appropriate for your Windows version (32-bit or 64-bit).

Run the installer and follow the instructions. Make sure to check the "Add Python to PATH" option during installation.

Once Python is installed, open the Command Prompt (search for "cmd" in the Start menu).

Type python and press Enter to open the Python interpreter. You should see the Python version and prompt (>>>) indicating that Python is successfully installed.
```
```
Enter the following command to check if tkinter is installed:

python
Copy code
import tkinter
If there are no errors, tkinter is already installed. Otherwise, you will receive an error message indicating that the module is not found.

If tkinter is not installed, you can install it using the following command:

pip install tkinter

This command will install the tkinter package for Python.
```

## Virtualbox environment

Pre setup Debian VM - [VirtualboxVM details](/VirtualboxVM/README.md) - Guide, Download links (md5sum)

## Typical recorded errors (errlog) in the syscon shell:

A = Fixed value

00-7F = Step number of power on sequence

80 = Poweron state

90 = Poweroff state

A0 = Power on immediatley after syscon reset

## Categories:

1 = System error
2 = Fatal error
3 = Fatal booting error
4 = Data error

------------------------------------------------

## Recorded errors:

A0022110 = MK I2C ERROR (OR OTHER CLOCK's ERRORS)

A0A02031 = Thermal monitor DI/DO not communicating to RSX (possible dead Diodes in RSX)

A0201B02 = RSX VRAM FAIL - Faulty vrams - Borked RSX VRAM, VDDIO reading on RSX is infinite - Dead RSX

A0201B01 = CELL - Low resistance on VDDIO (reading should be in megaohms), resistance readings near the tokins read higher than 4.5ohms = Dead core on the CELL

A0203010 = BE_INIT OR BE_POWGOOD OR CLOCK ERRORS

A0213011 =  BE_SPI CS ERROR

A0213013 = BE_SPI DI/DO ERROR - CELL not communicating to syscon via SPI (1.2V MC2_VDDIO and 1.2V BE_VCS no output) = Possible shorts on the line, check C4001 and trailing caps. Possible CELL dead?

A0232102 = IC6301 possible faulty - check other DC converters, caps etc in that power line from the schematics

A0003001 = POW_FAIL

A0302203 = SB_SPI DI/DO ERROR

A0313032 = SB_CLOCK OR INIT ERROR (can be related to the CELL solder balls not making proper connection and will most likely had previous errors like A0403034, A0404401) - check for voltages first!

A0401001 = BE VRAM Power Fail - running state possible tokins issues

A0401002 = RSX VRAM Power Fail - running state possible tokins issues

A0401301 = BE PLL Unlock

A0402120 = HDMI Error (IC2502)

A0403034, A0404402,A0404411 (RSX) = Poor BGA solder connections for RSX need reflow or reball ( you will see errors like - [POWERSEQ] Error : BitTraining RSX:RRAC:RX0:GLOBAL1:RX_STATUS )

A0403034, A0404401 (CELL) = Poor BGA solder connections for CELL need reflow or reball ( you will see errors like - [POWERSEQ] Error : BitTraining BE:RRAC:RX0:GLOBAL1:RX_STATUS )
(With the above errors you will get other errors with the BitTraining they are all related to the poor BGA connection or broken traces under the chips)

A0404002 = RSX_SPI DI/DO ERROR (Poor BGA connection for RSX can cause this error or DEAD RSX)

A0404411 = ERROR ON RSX SPI?

A0801001 = CELL Power on VRAM failure (Potential NEC tokins issue and VCC)

A0801002 = RSX Power on VRAM failure (Potential NEC tokins issue and VCC)

A0801200 = CELL overheating - poor thermal paste or no heatsink attached, GLOD symptoms

A0821200 = HDMI Power on failure (IC2502) - Sil9132CBU chip failure or related power line failure - check diodes,fuses and regulator IC2501

A0902203 = SB GLOD issues, system update to repair nand/nor hashes

A0093003 = CELL_POW_FAIL poweroff state (Potential NEC tokins issue and VCC or Dead/Short in the CELL)

A0093004 = RSX_POW_FAIL poweroff state (Potential NEC tokins issue and VCC or Dead/Short in the RSX (core reads 0.2 ohms))

## Notes on error codes

A0093003 and A0093004 (usually associate with nec tokin faults) have found to have issues with shorts on the PCB layer - COKxx boards seems to have a defect of the pcb layers (too much heating stresses the pcb layers) shorting on the VDD line to the Buck controllers (5v)
which causes leaking voltage.

Sometimes an error code can have an associate error code with it as seen with A0403034 (data error) and RS:RRAC:BX0:BX:FLEXIO_ID Bittraining errors = CELL cant talk or understand the RSX ID code (seen in swapping an 90nm to 65nm or 40nm)


## More in depth SYSCON Error codes meaning
[PS3Dev Wiki Syscon Error Codes](https://www.psdevwiki.com/ps3/Syscon_Error_Codes)
