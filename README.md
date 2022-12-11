# ps3syscon
PS3 syscon guide and fault finding

Required Python 2 or Python 3 - Linux/ps3_syscon_uart_script.py

Windows users 
  - [Windows/SysconReader/readme.md](/Windows/SysconReader/readme.md)
  - Windows/syscon.ps1 (PowerShell script)
    - Tested on Windows PowerShell 5.1 and PowerShell Core 7.2
    - Same syntax as the Python script
    - **Sherwood syscons not guaranteed to be working**

Tested on Linux with python - Follow guide for requirements

Pre setup Debian VM - [VirtualboxVM/PS3-SYSCON.ova.md](/VirtualboxVM/PS3-SYSCON.ova.md) - Download links, md5sum

## PS3-Syscon VM requirements

* Virtualbox 6.x, 7.x - Windows or Linux - [Virtualbox website download](https://www.virtualbox.org/wiki/Downloads)
* Virtualbox Extension pack required for USB access to the serial lead

Once virtualbox is installed, import the ova file as an appliance - login/ssh/http details are in the description of the import ova


## Typical recorded errors (errlog) in the syscon shell:

A = Fixed value

80 = Poweron state

A0 = Power on immediatley after syscon reset

Categories:

1 = System error
2 = Fatal error
3 = Fatal booting error
4 = Data error

------------------------------------------------

Recorded errors:

A003001 = POW_FAIL

A082120 = HDMI Power on failure (IC2502) - Sil9132CBU chip failure or related power line failure - check diodes,fuses and regulator IC2501

A0201B02 = RSX VRAM FAIL - Faulty vrams (core would read a 0.2 ohm reading)

A0801001 = CELL Power on VRAM failure

A0801002 = RSX Power on VRAM failure

A0093004 = RSX_POW_FAIL poweroff state

A0093003 CELL_POW_FAIL poweroff state

A0213013 = BE_SPI DI/DO ERROR - CELL not communicating to syscon via SPI (1.2V MC2_VDDIO and 1.2V BE_VCS no output) = Possible shorts on the line, check C4001 and trailing caps. Possible CELL dead?

A0213011 =  BE_SPI CS ERROR

A0203010 = BE_INIT OR BE_POWGOOD OR CLOCK ERRORS

A0801200 = CELL overheating - poor thermal paste or no heatsink attached, GLOD symptoms

A0404002 = RSX_SPI DI/DO ERROR

A0404411 = ERROR ON RSX SPI?

A0A02031 = Thermal monitor DI/DO not communicating to RSX (possible dead Diodes in RSX)

A0403034, A0404402,A0404411 = Poor BGA solder connections for RSX ( you will see errors like - [POWERSEQ] Error : BitTraining RSX:RRAC:RX0:GLOBAL1:RX_STATUS )

A0232102 = IC6301 faulty (1.5v RSX_VDDIO) or in that area

A0302203 = SB_SPI DI/DO ERROR

A0313032 = SB_CLOCK OR INIT ERROR

A0902203 = SB GLOD issues, system update to repair nand/nor hashes

A0022110 = MK I2C ERROR (OR OTHER CLOCK's ERRORS)

A0401001 = BE VRAM Power Fail - running state possible tokins issues

A0401002 = RSX VRAM Power Fail - running state possible tokins issues

A0402120 = HDMI Error (IC2502)

A0401301 = BE PLL Unlock

## More in depth SYSCON Error codes meaning
[PS3Dev Wiki Syscon Error Codes](https://www.psdevwiki.com/ps3/Error_Codes#SYSCON_Error_Codes)
