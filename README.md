# PS3 Syscon Tool

PS3 syscon guide, UART communication tool, and fault finding reference.

## Download

Pre-built binaries are available in the [go-gui/](go-gui/) folder:

| Platform | File | Size |
|----------|------|------|
| **macOS** | `ps3syscon-gui` | 31 MB |
| **Windows** | `ps3syscon-gui.exe` | 23 MB |

No Python or other runtime required - just download and run.

## Features

- Serial port selection with auto-detection and refresh
- SC Type selection (CXR, CXRF, SW)
- Send commands with full protocol handling
- AES-CBC authentication support
- Serial monitor window for diagnostics
- Help dialog with command reference
- Cross-platform GUI (macOS, Windows, Linux)

## Building from Source

Requires Go 1.21+ and CGO support.

```bash
cd go-gui

# Build for current platform
go build -ldflags="-s -w" .

# Cross-compile for Windows (requires mingw-w64)
GOOS=windows GOARCH=amd64 CGO_ENABLED=1 CC=x86_64-w64-mingw32-gcc go build -ldflags="-s -w -H windowsgui" -o ps3syscon-gui.exe .

# Cross-compile for Linux
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ps3syscon-gui-linux .
```

## Usage

1. Connect your UART adapter to the PS3 syscon
2. Launch the GUI application
3. Select the serial port from the dropdown (click Refresh if not shown)
4. Select SC Type:
   - **CXR** - External mode (most common)
   - **CXRF** - Internal mode (115200 baud)
   - **SW** - Sherwood syscons
5. Enter a command and click "Send Command"
6. Use "Auth" button to authenticate before protected commands

### Common Commands

**External mode (CXR):**
- `EEP GET <addr>` - Read EEPROM address
- `EEP SET <addr> <value>` - Write EEPROM address
- `ERRLOG GET 00` - Get error log (repeat 00-1F)

**Internal mode (CXRF):**
- `eepcsum` - Check EEPROM checksum
- `errlog` - Get error log
- `clearerrlog` - Clear error log
- `r <addr>` - Read from EEPROM
- `w <addr> <value>` - Write to EEPROM
- `fantbl` - Fan table operations
- `patchvereep` - Get patched version

See the [PS3-Uart-Guide-V2.pdf](PS3-Uart-Guide-V2.pdf) for detailed documentation.

---

## Syscon Error Codes Reference

### Error Code Format

`A0XXYYZZ` where:
- **A** = Fixed value
- **XX** = Step number (00-7F: power on sequence, 80: power on state, 90: power off state, A0: power on after syscon reset)
- **YY** = Category
- **ZZ** = Error code

### Categories

| Code | Meaning |
|------|---------|
| 1 | System error |
| 2 | Fatal error |
| 3 | Fatal booting error |
| 4 | Data error |

### Common Error Codes

| Code | Description | Possible Cause |
|------|-------------|----------------|
| `A0022110` | MK I2C ERROR | Clock errors |
| `A0A02031` | Thermal monitor DI/DO | Dead diodes in RSX |
| `A0201B02` | RSX VRAM FAIL | Faulty VRAM, dead RSX |
| `A0201B01` | CELL VDDIO | Low resistance on VDDIO, dead CELL core |
| `A0203010` | BE_INIT/POWGOOD/CLOCK | Clock errors |
| `A0213011` | BE_SPI CS ERROR | SPI chip select error |
| `A0213013` | BE_SPI DI/DO ERROR | CELL not communicating via SPI |
| `A0232102` | IC6301 fault | Check DC converters and caps |
| `A0003001` | POW_FAIL | Power failure |
| `A0302203` | SB_SPI DI/DO ERROR | Southbridge SPI error |
| `A0313032` | SB_CLOCK/INIT ERROR | CELL solder balls not connecting |
| `A0401001` | BE VRAM Power Fail | Tokins issues (running state) |
| `A0401002` | RSX VRAM Power Fail | Tokins issues (running state) |
| `A0401301` | BE PLL Unlock | PLL error |
| `A0402120` | HDMI Error | IC2502 fault |
| `A0403034` | BGA connection error | RSX/CELL needs reflow or reball |
| `A0404401` | BitTraining CELL | Poor CELL BGA connection |
| `A0404402` | BitTraining RSX | Poor RSX BGA connection |
| `A0404411` | RSX SPI ERROR | Poor RSX BGA or dead RSX |
| `A0404002` | RSX_SPI DI/DO ERROR | Poor BGA or dead RSX |
| `A0801001` | CELL VRAM failure | NEC tokins or VCC issue |
| `A0801002` | RSX VRAM failure | NEC tokins or VCC issue |
| `A0801200` | CELL overheating | Poor thermal paste, GLOD |
| `A0821200` | HDMI Power failure | Sil9132CBU or IC2501 |
| `A0902203` | SB GLOD | System update needed |
| `A0093003` | CELL_POW_FAIL | Tokins, VCC, or dead CELL |
| `A0093004` | RSX_POW_FAIL | Tokins, VCC, or dead RSX |

### Notes on Error Codes

- **A0093003 / A0093004**: Often associated with NEC tokin faults, but can also indicate shorts on PCB layers. COKxx boards may have defects where heating stresses cause shorts on VDD line to Buck controllers (5V).

- **A0403034 with BitTraining errors**: When seen with `RS:RRAC:BX0:BX:FLEXIO_ID` errors, indicates CELL can't communicate with RSX (common when swapping 90nm to 65nm/40nm chips).

### More Information

- [PS3Dev Wiki - Syscon Error Codes](https://www.psdevwiki.com/ps3/Syscon_Error_Codes)
- [Syscon Error Codes PDF](Syscon-error-log-codes.pdf)

---

## Documentation

- [PS3-Uart-Guide-V1.pdf](PS3-Uart-Guide-V1.pdf) - Original guide
- [PS3-Uart-Guide-V2.pdf](PS3-Uart-Guide-V2.pdf) - Updated guide
- [Other-Docs/](Other-Docs/) - Additional documentation
- [PS3-Serial-Connection-Points/](PS3-Serial-Connection-Points/) - Connection diagrams

## License

This project is for educational and repair purposes only.
