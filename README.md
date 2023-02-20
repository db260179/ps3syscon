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

A0201B02 = RSX VRAM FAIL - Faulty vrams - Borked RSX VRAM, NEC tokins, caps, a short or FBVDDQ power line

A0203010 = BE_INIT OR BE_POWGOOD OR CLOCK ERRORS

A0213011 =  BE_SPI CS ERROR

A0213013 = BE_SPI DI/DO ERROR - CELL not communicating to syscon via SPI (1.2V MC2_VDDIO and 1.2V BE_VCS no output) = Possible shorts on the line, check C4001 and trailing caps. Possible CELL dead?

A0232102 = IC6301 possible faulty - check other DC converters, caps etc in that power line from the schematics

A0003001 = POW_FAIL

A0302203 = SB_SPI DI/DO ERROR

A0313032 = SB_CLOCK OR INIT ERROR

A0401001 = BE VRAM Power Fail - running state possible tokins issues

A0401002 = RSX VRAM Power Fail - running state possible tokins issues

A0401301 = BE PLL Unlock

A0402120 = HDMI Error (IC2502)

A0403034, A0404402,A0404411 = Poor BGA solder connections for RSX ( you will see errors like - [POWERSEQ] Error : BitTraining RSX:RRAC:RX0:GLOBAL1:RX_STATUS )

A0404002 = RSX_SPI DI/DO ERROR

A0404411 = ERROR ON RSX SPI?

A0801001 = CELL Power on VRAM failure (Potential NEC tokins issue and VCC)

A0801002 = RSX Power on VRAM failure (Potential NEC tokins issue and VCC)

A0801200 = CELL overheating - poor thermal paste or no heatsink attached, GLOD symptoms

A0821200 = HDMI Power on failure (IC2502) - Sil9132CBU chip failure or related power line failure - check diodes,fuses and regulator IC2501

A0902203 = SB GLOD issues, system update to repair nand/nor hashes

A0093003 = CELL_POW_FAIL poweroff state (Potential NEC tokins issue and VCC)

A0093004 = RSX_POW_FAIL poweroff state (Potential NEC tokins issue and VCC)


## More in depth SYSCON Error codes meaning
[PS3Dev Wiki Syscon Error Codes](https://www.psdevwiki.com/ps3/Syscon_Error_Codes)
