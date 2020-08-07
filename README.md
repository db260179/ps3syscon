# ps3syscon
PS3 syscon guide and fault finding

Required Python 2 to use (python 3 support is broken at the moment) and modules serial and crypto

Recorded errors (errlog) in the syscon shell:

POWER ERRORS:
0003001 POW_FAIL
A0093004 RSX_POW_FAIL
A0093003 CELL_POW_FAIL

BE ERRORS:
A0213013 BE_SPI DI/DO ERROR - CELL not communicating to syscon via SPI (1.2V MC2_VDDIO and 1.2V BE_VCS no output) = Dead CELL
A0213011 BE_SPI CS ERROR
A0203010 BE_INIT OR BE_POWGOOD OR CLOCK ERRORS
A0801200 CELL overheating - poor thermal paste or no heatsink attached

RSX ERRORS:
A0404002 RSX_SPI DI/DO ERROR
A0404411 - ERROR ON RSX SPI?

A0403034, A0404402,A0404411 - Poor BGA solder connections for RSX ( you will see errors like - [POWERSEQ] Error : BitTraining RSX:RRAC:RX0:GLOBAL1:RX_STATUS )

A0232102 - IC6301 faulty (1.5v RSX_VDDIO) or in that area

SB ERRORS:
A0302203 SB_SPI DI/DO ERROR
A0313032 SB_CLOCK OR INIT ERROR
A0902203 SB GLOD issues, system update to repair Blue ray or wifi related issues

OTHERS:
A0022110 MK I2C ERROR (OR OTHER CLOCK's ERRORS)

A0401001 - BE VRAM Power Fail. It can be NEC Tokins
A0401002 - RSX VRAM Power Fail. It can be NEC Tokins

A0402120 - HDMI Error (IC2502)
A0401301 - BE PLL Unlock
