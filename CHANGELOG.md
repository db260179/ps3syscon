# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2024-12-15

### Added
- **New Go/Fyne GUI** - Complete rewrite in Go with Fyne framework
  - Single static binary, no runtime dependencies
  - Pre-built binaries for macOS (31MB) and Windows (23MB)
  - Cross-platform support (macOS, Windows, Linux)
- ACE branding header with logo support
- Serial monitor window for real-time diagnostics
- Improved error handling and user feedback

### Changed
- Replaced Python/tkinter GUI with Go/Fyne implementation
- Updated README with new installation and usage instructions
- Reorganized error codes reference into table format

### Removed
- Legacy Python scripts (`Linux/`, `Windows/`, `python-gui/` folders)
- VirtualboxVM documentation (outdated)
- PowerShell script (`syscon.ps1`)
- SysconReader Windows utility

### Technical
- AES-CBC authentication using Go's crypto/aes standard library
- Serial communication via go.bug.st/serial
- GUI rendering via Fyne v2 framework

---

## [1.x] - Previous Releases

### [1.5.0] - Python GUI Updates
- Added diagnose serial output feature with separate window
- Added psdevwiki link for error codes
- Added serial port refresh button
- Fixed pyinstaller finding secondary scripts
- Updated Linux and Windows executables

### [1.4.0] - Python GUI Improvements
- Added window resize feature
- Added more internal and external commands to help
- Made buttons more compact
- Changed AES reference to use pycryptodomex

### [1.3.0] - GUI Features
- Added function to scan for available serial ports
- Added serial port examples in UI
- Added syscon type selection box

### [1.2.0] - Initial GUI
- Created Python tkinter GUI for UART script
- Added Linux and Windows standalone executables via PyInstaller

### [1.1.0] - Script Improvements
- Added PowerShell script for Windows
- Added SysconReader utility
- Improved error handling

### [1.0.0] - Initial Release
- Linux Python UART script
- Basic syscon communication
- Error code documentation
