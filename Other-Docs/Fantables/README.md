### Fan thermal config settings

In depth config from https://www.psdevwiki.com/ps3/Syscon_Thermal_Configs

My supplied configs are just my personal tweaks, please adjust based on reading the above link.

## Notes on commands used

Changing with set will not change checksum - temporary set in the NVRAM, but changing with the setini will adjusted in the syscon address.

Fix the checksum using the 'eepcsum' command in the syscon shell to view the correct value - Write the correct value based on the eepcsum reading

eepcsum
Addr:0x000032fe should be 0x528c
Addr:0x000034fe should be 0x7115
sum:0x0100
Addr:0x000039fe should be 0x0038
Addr:0x00003dfe should be 0x00ff
Addr:0x00003ffe should be 0x00ff

Example only - 'w 34fe 15 71' if the sum value was shown as '0x7115'
