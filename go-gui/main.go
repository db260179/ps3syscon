package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/hex"
	"fmt"
	"image/color"
	"os"
	"path/filepath"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
	"go.bug.st/serial"
)

// Crypto keys for PS3 Syscon authentication
var (
	sc2tb       = mustDecodeHex("71f03f184c01c5ebc3f6a22a42ba9525") // Syscon to TestBench Key
	tb2sc       = mustDecodeHex("907e730f4d4e0a0b7b75f030eb1d9d36") // TestBench to Syscon Key
	authValue   = mustDecodeHex("3350BD7820345C29056A223BA220B323") // 0x45B8
	zeroIV      = mustDecodeHex("00000000000000000000000000000000")
	auth1rHdr   = mustDecodeHex("10100000FFFFFFFF0000000000000000")
	auth2Header = mustDecodeHex("10010000000000000000000000000000")
)

func mustDecodeHex(s string) []byte {
	b, err := hex.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return b
}

// PS3UART handles serial communication with PS3 Syscon
type PS3UART struct {
	port        serial.Port
	scType      string
	serialSpeed int
}

// NewPS3UART creates a new PS3UART connection
func NewPS3UART(portName, scType string, serialSpeed int) (*PS3UART, error) {
	mode := &serial.Mode{
		BaudRate: serialSpeed,
		DataBits: 8,
		Parity:   serial.NoParity,
		StopBits: serial.OneStopBit,
	}

	port, err := serial.Open(portName, mode)
	if err != nil {
		return nil, fmt.Errorf("failed to open serial port: %w", err)
	}

	port.SetReadTimeout(100 * time.Millisecond)

	return &PS3UART{
		port:        port,
		scType:      scType,
		serialSpeed: serialSpeed,
	}, nil
}

// Close closes the serial connection
func (p *PS3UART) Close() error {
	if p.port != nil {
		return p.port.Close()
	}
	return nil
}

// aesDecryptCBC decrypts data using AES-CBC
func aesDecryptCBC(key, iv, data []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	if len(data)%aes.BlockSize != 0 {
		return nil, fmt.Errorf("ciphertext is not a multiple of block size")
	}

	mode := cipher.NewCBCDecrypter(block, iv)
	decrypted := make([]byte, len(data))
	mode.CryptBlocks(decrypted, data)

	return decrypted, nil
}

// aesEncryptCBC encrypts data using AES-CBC
func aesEncryptCBC(key, iv, data []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	if len(data)%aes.BlockSize != 0 {
		return nil, fmt.Errorf("plaintext is not a multiple of block size")
	}

	mode := cipher.NewCBCEncrypter(block, iv)
	encrypted := make([]byte, len(data))
	mode.CryptBlocks(encrypted, data)

	return encrypted, nil
}

// send writes ASCII data to serial port
func (p *PS3UART) send(data string) error {
	_, err := p.port.Write([]byte(data))
	return err
}

// receive reads available data from serial port
func (p *PS3UART) receive() (string, error) {
	buf := make([]byte, 4096)
	var result []byte

	for {
		n, err := p.port.Read(buf)
		if err != nil {
			break
		}
		if n == 0 {
			break
		}
		result = append(result, buf[:n]...)
	}

	return string(result), nil
}

// CommandResult holds the result of a command execution
type CommandResult struct {
	Code uint32
	Data []string
}

// Command sends a command and returns the result
func (p *PS3UART) Command(cmd string, waitSec float64) CommandResult {
	switch p.scType {
	case "CXR":
		return p.commandCXR(cmd, waitSec)
	case "SW":
		return p.commandSW(cmd, waitSec)
	default:
		return p.commandCXRF(cmd, waitSec)
	}
}

func (p *PS3UART) commandCXR(cmd string, waitSec float64) CommandResult {
	length := len(cmd)
	checksum := 0
	for _, c := range cmd {
		checksum += int(c)
	}
	checksum %= 0x100

	if length <= 10 {
		p.send(fmt.Sprintf("C:%02X:%s\r\n", checksum, cmd))
	} else {
		j := 10
		p.send(fmt.Sprintf("C:%02X:%s", checksum, cmd[0:j]))
		for i := length - j; i > 15; i -= 15 {
			p.send(cmd[j : j+15])
			j += 15
		}
		p.send(cmd[j:] + "\r\n")
	}

	time.Sleep(time.Duration(waitSec * float64(time.Second)))
	answer, _ := p.receive()
	answer = strings.TrimSpace(answer)

	parts := strings.Split(answer, ":")
	if len(parts) != 3 {
		return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Answer length"}}
	}

	checksum = 0
	for _, c := range parts[2] {
		checksum += int(c)
	}
	checksum %= 0x100

	if parts[0] != "R" && parts[0] != "E" {
		return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Magic"}}
	}
	if parts[1] != fmt.Sprintf("%02X", checksum) {
		return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Checksum"}}
	}

	data := strings.Split(parts[2], " ")
	if (parts[0] == "R" && len(data) < 2) || (parts[0] == "E" && len(data) != 2) {
		return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Data length"}}
	}

	code := parseHexUint32(data[1])
	if data[0] != "OK" || len(data) < 2 {
		return CommandResult{Code: code, Data: []string{}}
	}
	return CommandResult{Code: code, Data: data[2:]}
}

func (p *PS3UART) commandSW(cmd string, waitSec float64) CommandResult {
	length := len(cmd)
	if length >= 0x40 {
		result := p.Command("SETCMDLONG FF FF", 1)
		if result.Code != 0 {
			return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Setcmdlong"}}
		}
	}

	checksum := 0
	for _, c := range cmd {
		checksum += int(c)
	}
	checksum %= 0x100

	p.send(fmt.Sprintf("%s:%02X\r\n", cmd, checksum))

	time.Sleep(time.Duration(waitSec * float64(time.Second)))
	answer, _ := p.receive()
	answer = strings.TrimSpace(answer)

	lines := strings.Split(answer, "\n")
	for i, line := range lines {
		line = strings.ReplaceAll(line, "\n", "")
		parts := strings.SplitN(line, ":", 2)
		if len(parts) != 2 {
			return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Answer length"}}
		}

		checksum = 0
		for _, c := range parts[0] {
			checksum += int(c)
		}
		checksum %= 0x100

		if parts[1] != fmt.Sprintf("%02X", checksum) {
			return CommandResult{Code: 0xFFFFFFFF, Data: []string{"Checksum"}}
		}
		lines[i] = parts[0] + "\n"
	}

	ret := strings.Split(strings.ReplaceAll(lines[len(lines)-1], "\n", ""), " ")
	if len(ret) < 2 || len(ret[1]) != 8 {
		return CommandResult{Code: 0, Data: lines}
	} else if len(lines) == 1 {
		return CommandResult{Code: parseHexUint32(ret[1]), Data: ret[2:]}
	}
	return CommandResult{Code: parseHexUint32(ret[1]), Data: lines[:len(lines)-1]}
}

func (p *PS3UART) commandCXRF(cmd string, waitSec float64) CommandResult {
	p.send(cmd + "\r\n")
	time.Sleep(time.Duration(waitSec * float64(time.Second)))
	answer, _ := p.receive()
	answer = strings.TrimSpace(answer)
	return CommandResult{Code: 0, Data: []string{answer}}
}

func parseHexUint32(s string) uint32 {
	var val uint32
	fmt.Sscanf(s, "%x", &val)
	return val
}

// bytesEqual compares two byte slices
func bytesEqual(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

// Auth performs authentication with the Syscon
func (p *PS3UART) Auth() string {
	if p.scType == "CXR" || p.scType == "SW" {
		auth1r := p.Command("AUTH1 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)
		if auth1r.Code == 0 && len(auth1r.Data) > 0 {
			auth1rBytes, err := hex.DecodeString(auth1r.Data[0])
			if err != nil {
				return "Auth1 response decode error"
			}

			if len(auth1rBytes) >= 0x40 && bytesEqual(auth1rBytes[0:0x10], auth1rHdr) {
				data, err := aesDecryptCBC(sc2tb, zeroIV, auth1rBytes[0x10:0x40])
				if err != nil {
					return "Decryption error"
				}

				if bytesEqual(data[0x8:0x10], zeroIV[0:0x8]) &&
					bytesEqual(data[0x10:0x20], authValue) &&
					bytesEqual(data[0x20:0x30], zeroIV) {

					newData := make([]byte, 0x30)
					copy(newData[0:0x8], data[0x8:0x10])
					copy(newData[0x8:0x10], data[0x0:0x8])
					// Rest is zeros

					auth2Body, err := aesEncryptCBC(tb2sc, zeroIV, newData)
					if err != nil {
						return "Encryption error"
					}

					auth2Cmd := "AUTH2 " + strings.ToUpper(hex.EncodeToString(append(auth2Header, auth2Body...)))
					auth2r := p.Command(auth2Cmd, 1)
					if auth2r.Code == 0 {
						return "Auth successful"
					}
					return "Auth failed"
				}
				return "Auth1 response body invalid"
			}
			return "Auth1 response header invalid"
		}
		return "Auth1 response invalid"
	}

	// CXRF mode
	scopen := p.Command("scopen", 1)
	if len(scopen.Data) > 0 && strings.Contains(scopen.Data[0], "SC_READY") {
		auth1r := p.Command("10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)
		if len(auth1r.Data) > 0 {
			parts := strings.Split(auth1r.Data[0], "\r")
			if len(parts) > 1 && len(parts[1]) > 1 {
				auth1rHex := parts[1][1:]
				if len(auth1rHex) == 128 {
					auth1rBytes, _ := hex.DecodeString(auth1rHex)
					if bytesEqual(auth1rBytes[0:0x10], auth1rHdr) {
						data, _ := aesDecryptCBC(sc2tb, zeroIV, auth1rBytes[0x10:0x40])
						if bytesEqual(data[0x8:0x10], zeroIV[0:0x8]) &&
							bytesEqual(data[0x10:0x20], authValue) &&
							bytesEqual(data[0x20:0x30], zeroIV) {

							newData := make([]byte, 0x30)
							copy(newData[0:0x8], data[0x8:0x10])
							copy(newData[0x8:0x10], data[0x0:0x8])

							auth2Body, _ := aesEncryptCBC(tb2sc, zeroIV, newData)
							auth2Cmd := strings.ToUpper(hex.EncodeToString(append(auth2Header, auth2Body...)))
							auth2r := p.Command(auth2Cmd, 1)
							if len(auth2r.Data) > 0 && strings.Contains(auth2r.Data[0], "SC_SUCCESS") {
								return "Auth successful"
							}
							return "Auth failed"
						}
						return "Auth1 response body invalid"
					}
					return "Auth1 response header invalid"
				}
				return "Auth1 response invalid"
			}
		}
	}
	return "scopen response invalid"
}

// getSerialPorts returns a list of available serial ports
func getSerialPorts() []string {
	ports, err := serial.GetPortsList()
	if err != nil {
		return []string{}
	}
	return ports
}

// getLogoPath finds the logo file path
func getLogoPath() string {
	// Check current directory
	if _, err := os.Stat("ace_logo.png"); err == nil {
		return "ace_logo.png"
	}
	// Check executable directory
	exe, err := os.Executable()
	if err == nil {
		dir := filepath.Dir(exe)
		logoPath := filepath.Join(dir, "ace_logo.png")
		if _, err := os.Stat(logoPath); err == nil {
			return logoPath
		}
	}
	return ""
}

// createBrandingHeader creates the header with logo and text
func createBrandingHeader() fyne.CanvasObject {
	brandingText := canvas.NewText("Get ya'self reballed by", color.RGBA{100, 100, 100, 255})
	brandingText.TextSize = 14
	brandingText.Alignment = fyne.TextAlignCenter

	logoPath := getLogoPath()
	if logoPath != "" {
		logo := canvas.NewImageFromFile(logoPath)
		logo.SetMinSize(fyne.NewSize(240, 80))
		logo.FillMode = canvas.ImageFillContain

		header := container.NewVBox(
			container.NewCenter(brandingText),
			container.NewCenter(logo),
			widget.NewSeparator(),
		)
		return header
	}

	// Fallback: just show text with ACE in color
	aceText := canvas.NewText("ACE", color.RGBA{120, 180, 120, 255})
	aceText.TextSize = 24
	aceText.TextStyle = fyne.TextStyle{Bold: true}
	aceText.Alignment = fyne.TextAlignCenter

	header := container.NewVBox(
		container.NewCenter(brandingText),
		container.NewCenter(aceText),
		widget.NewSeparator(),
	)
	return header
}

func main() {
	myApp := app.New()
	myWindow := myApp.NewWindow("PS3UART GUI")
	myWindow.Resize(fyne.NewSize(600, 500))

	// Branding header
	header := createBrandingHeader()

	// Port selection
	portSelect := widget.NewSelect(getSerialPorts(), nil)
	portSelect.PlaceHolder = "Select serial port"

	refreshBtn := widget.NewButton("Refresh", func() {
		portSelect.Options = getSerialPorts()
		portSelect.Refresh()
	})

	portRow := container.NewBorder(nil, nil, nil, refreshBtn, portSelect)

	// SC Type selection
	scTypeSelect := widget.NewSelect([]string{"CXR", "CXRF", "SW"}, nil)
	scTypeSelect.SetSelected("CXR")

	// Command entry
	commandEntry := widget.NewEntry()
	commandEntry.SetPlaceHolder("Enter command (e.g., EEP GET 00)")

	// Output text
	outputText := widget.NewMultiLineEntry()
	outputText.SetMinRowsVisible(10)
	outputText.Wrapping = fyne.TextWrapWord

	// Send command handler
	sendCmd := func() {
		if portSelect.Selected == "" || scTypeSelect.Selected == "" {
			dialog.ShowError(fmt.Errorf("please select serial port and SC type"), myWindow)
			return
		}

		serialSpeed := 57600
		if scTypeSelect.Selected == "CXRF" {
			serialSpeed = 115200
		}

		ps3, err := NewPS3UART(portSelect.Selected, scTypeSelect.Selected, serialSpeed)
		if err != nil {
			dialog.ShowError(err, myWindow)
			return
		}
		defer ps3.Close()

		result := ps3.Command(commandEntry.Text, 1)
		if result.Code == 0xFFFFFFFF {
			dialog.ShowError(fmt.Errorf("command failed: %s", result.Data[0]), myWindow)
			return
		}

		var output string
		switch scTypeSelect.Selected {
		case "CXR":
			output = fmt.Sprintf("%08X %s", result.Code, strings.Join(result.Data, " "))
		case "SW":
			if len(result.Data) > 0 && !strings.Contains(result.Data[0], "\n") {
				output = fmt.Sprintf("%08X %s", result.Code, strings.Join(result.Data, " "))
			} else {
				output = fmt.Sprintf("%08X\n%s", result.Code, strings.Join(result.Data, ""))
			}
		default:
			if len(result.Data) > 0 {
				output = result.Data[0]
			}
		}

		outputText.SetText(outputText.Text + output + "\n")
	}

	// Auth handler
	authCmd := func() {
		if portSelect.Selected == "" || scTypeSelect.Selected == "" {
			dialog.ShowError(fmt.Errorf("please select serial port and SC type"), myWindow)
			return
		}

		serialSpeed := 57600
		if scTypeSelect.Selected == "CXRF" {
			serialSpeed = 115200
		}

		ps3, err := NewPS3UART(portSelect.Selected, scTypeSelect.Selected, serialSpeed)
		if err != nil {
			dialog.ShowError(err, myWindow)
			return
		}
		defer ps3.Close()

		result := ps3.Auth()
		dialog.ShowInformation("Authentication Result", result, myWindow)
	}

	// Help handler
	showHelp := func() {
		helpText := `External mode:
EEP GET (get EEPROM address)
EEP SET (set EEPROM address value)
ERRLOG GET 00 (get errorlog from code 0 - repeat until 1F)

Internal mode:
eepcsum (check EEPROM checksum)
errlog (get errlog)
clearerrlog (clear errorlog)
r (read from eeprom address)
w (write to eeprom address)
fantbl (get/set/getini/setini/gettable/settable)
patchvereep (get patched version)

Read the PS3-Uart-Guide-V2.pdf for further information`

		dialog.ShowInformation("Available Commands", helpText, myWindow)
	}

	// Buttons
	sendBtn := widget.NewButton("Send Command", sendCmd)
	authBtn := widget.NewButton("Auth", authCmd)
	helpBtn := widget.NewButton("Help", showHelp)

	serialMonitorBtn := widget.NewButton("Serial Monitor", func() {
		openSerialMonitor(myApp, portSelect.Selected, scTypeSelect.Selected)
	})

	btnRow1 := container.NewGridWithColumns(2, sendBtn, authBtn)
	btnRow2 := container.NewGridWithColumns(2, helpBtn, serialMonitorBtn)

	// Layout
	formContent := container.NewVBox(
		widget.NewLabel("Serial Port:"),
		portRow,
		widget.NewLabel("SC Type:"),
		scTypeSelect,
		widget.NewLabel("Command:"),
		commandEntry,
		widget.NewLabel("Output:"),
		outputText,
		btnRow1,
		btnRow2,
	)

	content := container.NewBorder(header, nil, nil, nil,
		container.NewPadded(formContent),
	)

	myWindow.SetContent(content)
	myWindow.ShowAndRun()
}

// openSerialMonitor opens the serial monitor window
func openSerialMonitor(myApp fyne.App, defaultPort, scType string) {
	monitorWindow := myApp.NewWindow("Serial Monitor")
	monitorWindow.Resize(fyne.NewSize(500, 400))

	portSelect := widget.NewSelect(getSerialPorts(), nil)
	if defaultPort != "" {
		portSelect.SetSelected(defaultPort)
	}

	baudSelect := widget.NewSelect([]string{"57600", "115200"}, nil)
	if scType == "CXRF" {
		baudSelect.SetSelected("115200")
	} else {
		baudSelect.SetSelected("57600")
	}

	outputText := widget.NewMultiLineEntry()
	outputText.SetMinRowsVisible(15)
	outputText.Wrapping = fyne.TextWrapWord

	var port serial.Port
	var monitoring bool
	var stopChan chan struct{}

	startBtn := widget.NewButton("Start", nil)
	stopBtn := widget.NewButton("Stop", nil)
	stopBtn.Disable()

	startBtn.OnTapped = func() {
		if portSelect.Selected == "" {
			dialog.ShowError(fmt.Errorf("please select a serial port"), monitorWindow)
			return
		}

		baudRate := 57600
		if baudSelect.Selected == "115200" {
			baudRate = 115200
		}

		mode := &serial.Mode{
			BaudRate: baudRate,
			DataBits: 8,
			Parity:   serial.NoParity,
			StopBits: serial.OneStopBit,
		}

		var err error
		port, err = serial.Open(portSelect.Selected, mode)
		if err != nil {
			dialog.ShowError(err, monitorWindow)
			return
		}

		port.SetReadTimeout(100 * time.Millisecond)
		monitoring = true
		stopChan = make(chan struct{})

		startBtn.Disable()
		stopBtn.Enable()
		portSelect.Disable()
		baudSelect.Disable()

		go func() {
			buf := make([]byte, 1024)
			for monitoring {
				select {
				case <-stopChan:
					return
				default:
					n, err := port.Read(buf)
					if err == nil && n > 0 {
						text := string(buf[:n])
						outputText.SetText(outputText.Text + text)
					}
				}
			}
		}()
	}

	stopBtn.OnTapped = func() {
		monitoring = false
		if stopChan != nil {
			close(stopChan)
		}
		if port != nil {
			port.Close()
		}

		startBtn.Enable()
		stopBtn.Disable()
		portSelect.Enable()
		baudSelect.Enable()
	}

	monitorWindow.SetOnClosed(func() {
		if monitoring {
			stopBtn.OnTapped()
		}
	})

	content := container.NewVBox(
		widget.NewLabel("Serial Port:"),
		portSelect,
		widget.NewLabel("Baud Rate:"),
		baudSelect,
		container.NewGridWithColumns(2, startBtn, stopBtn),
		widget.NewLabel("Output:"),
		outputText,
	)

	monitorWindow.SetContent(content)
	monitorWindow.Show()
}
