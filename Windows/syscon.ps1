#!/usr/bin/env pwsh
<#
	PS3 Syscon UART script
	
	Based on ps3_syscon_uart_script.py by db260179
	
	PowerShell version by redcyclone 
#>

$SerialPort = $Args[0]	# Serial port
$Type = $Args[1]	# Communication type
$AuthOK = $False	# Authenticated successfully?

# Keys and etc.
$SC2TB = [byte[]] -split ("71f03f184c01c5ebc3f6a22a42ba9525" -replace '..', '0x$& ') # Syscon to TestBench Key (0x130 xor 0x4578)
$TB2SC = [byte[]] -split ("907e730f4d4e0a0b7b75f030eb1d9d36" -replace '..', '0x$& ') # TestBench to Syscon Key (0x130 xor 0x4588)
$Value = [byte[]] -split ("3350BD7820345C29056A223BA220B323" -replace '..', '0x$& ') # 0x45B8
$Zero  = [byte[]] -split ("00000000000000000000000000000000" -replace '..', '0x$& ') # 0
$Auth1R_Header = [byte[]] -split ("10100000FFFFFFFF0000000000000000" -replace '..', '0x$& ') # AUTH1 response header
$Auth2Header = [byte[]] -split ("10010000000000000000000000000000" -replace '..', '0x$& ')   # AUTH2 header

# -----------------------------------------------------------------------------------------------------------------------------

# Command line checks
If(($Type -eq "CXR") -or ($Type -eq "SW")) {
	$BaudRate = 57600
}
ElseIf($Type -eq "CXRF") {
	$BaudRate = 115200
}
Else {
	Write-Host "Usage: " -ForegroundColor Red -NoNewline
	Write-Host "./syscon.ps1 " -ForegroundColor Yellow -NoNewline
	Write-Host "[PORT] [Type]`n"
	Write-Host "Types available: "-ForegroundColor Cyan -NoNewline
	Write-Host "CXR CXRF SW" -ForegroundColor White
	Write-Host "  CXR  = Mullion external" -ForegroundColor White
	Write-Host "  CXRF = Mullion internal " -ForegroundColor White
	Write-Host "  SW   = Sherwood (Not tested!) " -ForegroundColor White -NoNewline
	Write-Host "(CECHL onwards, except CECHM with DIA-001 board)" -ForegroundColor Yellow
	Write-Host "`nCheck https://github.com/db260179/ps3syscon/blob/master/PS3-Uart-Guide.pdf before use!!" -ForegroundColor Yellow
	Exit
}

# Configure and open serial port

$Port = New-Object System.IO.Ports.SerialPort $SerialPort, $BaudRate, None, 8, One
$Port.ReadTimeout = 1000
Try {
	$Port.Open()
} Catch [Exception] {
	Write-Host "Error: $_" -ForegroundColor Red
	Exit
}

# -----------------------------------------------------------------------------------------------------------------------------

# Sends a command over the serial port with the correct structure
Function Serial-Send {
	Param ($Cmd)
	If($Type -eq "CXR") {
		# Calculate checksum
		$Checksum = 0
		[System.Text.Encoding]::ASCII.GetBytes($Cmd) | ForEach-Object { $Checksum += $_ }
		$Checksum %= 0x100
		# If command is greater than 10 (Header + checksum + command equals 16), divide command in blocks of 16 bytes each
		If($Cmd.Length -le 10) {
			$Port.WriteLine("C:" + $($Checksum | ForEach-Object ToString "X2") + ":" + $Cmd + "`r`n")
		}
		Else {
			$j = 10
			$TrimCmd = "C:" + $($Checksum | ForEach-Object ToString "X2") + ":" + $($Cmd[0..$j] -join '')
			$Port.Write($TrimCmd)
			For($i = $Cmd.Length - $j;$i -gt 16; $i -= 16) {
				$TrimCmd = $($Cmd[$($j+1)..$($j+16)] -join '')
				$Port.Write($TrimCmd)
				$j += 16
			}
			$TrimCmd = $($Cmd[$($j+1)..$($Cmd.Length)] -join '') + "`r`n"
			$Port.WriteLine($TrimCmd)
		}
	} ElseIf ($Type -eq "SW") {
		# Haven't tested this yet. I don't own a SW syscon PS3. Probably works though...
		If($Cmd.Length -ge 0x40) {
			$Port.WriteLine("SETCMDLONG FF FF")
			Start-Sleep -M 500
			$Result = Serial-Receive
			If(!($Result.Split(' ')[1] -like "*00000000*")) {
				Write-Host "SETCMDLONG error!" -ForegroundColor Red
				Return
			}
		}
		$Checksum = 0
		[System.Text.Encoding]::ASCII.GetBytes($Cmd) | ForEach-Object { $Checksum += $_ }
		$Checksum %= 0x100
		$Port.WriteLine($Cmd + ":" + $($Checksum | ForEach-Object ToString "X2") + "`r`n")
	} Else {
		$Port.WriteLine($Cmd + "`r`n")
	}
	# Wait a bit for data response
	Start-Sleep -M 500
}

# Receives data from the serial port and returns as text
Function Serial-Receive {
	# Wait at least 5 seconds for data to be available
	$Timeout = 0
	While(($Port.BytesToRead -eq 0) -and ($Timeout -ne 5)) { Start-Sleep -S 1; $Timeout++ }
	If($Timeout -eq 5) {
		Write-Host "`nError: Data receive timeout!" -ForegroundColor Red
		Write-Host "`nNo data was received in at least 5 seconds." -ForegroundColor Red
		Write-Host "This means something is wrong with the wiring, serial port/converter or the PS3." -ForegroundColor Red
		Write-Host "Check your wiring and try running the script again." -ForegroundColor Red
		$Port.Close()
		$Port.Dispose()
		Exit
	}
	# Read available data to a byte array, convert to string and return
	[byte[]]$Buf = @()
	While($Port.BytesToRead -gt 0) {
		$Buf += $Port.ReadByte()
	}
	If($Type -eq "CXR") {
		$Result = [System.Text.Encoding]::ASCII.GetString($Buf)
		$SplitResult = $Result.Split(" ")
		If($SplitResult[0] -like "*:*:*") {
			Return $SplitResult[1..$SplitResult.Length]
		} Else {
			Return $Result
		}
	} Else {
		Return [System.Text.Encoding]::ASCII.GetString($Buf)
	}
}

# Decrypts data
Function Syscon-Decrypt {
	Param ($Key, $IV, $Data)
	$AES = New-Object "System.Security.Cryptography.AesManaged"
	$AES.Mode = [System.Security.Cryptography.CipherMode]::CBC
	$AES.Key = $Key
	$AES.IV = $IV
	$AES.Padding = "None"
	$AESDec = $AES.CreateDecryptor();
	Return $AESDec.TransformFinalBlock($Data[16..63], 0, $Data[16..63].Length)
}

# Encrypts data
Function Syscon-Encrypt {
	Param ($Key, $IV, $Data)
	$AES = New-Object "System.Security.Cryptography.AesManaged"
	$AES.Mode = [System.Security.Cryptography.CipherMode]::CBC
	$AES.Key = $Key
	$AES.IV = $IV
	$AES.Padding = "None"
	$AESEnc = $AES.CreateEncryptor()
	Return $AESEnc.TransformFinalBlock($NewData, 0, $NewData.Length)
}

# Authenticates with the Syscon.
Function Syscon-Auth {
	Write-Host ""
	If(($Type -eq "CXR") -or ($Type -eq "SW")) {
		Write-Host "Sending AUTH1..."
		Serial-Send "AUTH1 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
		$Result = $(Serial-Receive)[1].Replace("`n", "")
		# Check if response length is 128
		If($Result.Length -eq 128) {
			Write-Host "AUTH1 OK." -ForegroundColor Yellow
			$BinResult = [byte[]] -split ($Result -replace '..', '0x$& ')
			# Check if the response header is an AUTH1 response header
			If(!(Compare-Object $BinResult[0..15] $Auth1R_Header)) {
				# Decrypt the data
				$Data = Syscon-Decrypt $SC2TB $Zero $BinResult
				# Check if the decrypted data is correct
				If(!(Compare-Object $Data[8..15] $Zero[8..15]) -and !(Compare-Object $Data[16..31] $Value) -and !(Compare-Object $Data[32..47] $Zero)) {
					# Reconstruct the data, encrypt and send as an AUTH2 command
					[byte[]]$NewData = @()
					$NewData += $Data[8..15]
					$NewData += $Data[0..7]
					$NewData += $Zero
					$NewData += $Zero
					
					$Auth2Body = Syscon-Encrypt $TB2SC $Zero $NewData
					
					Write-Host "Sending AUTH2..."
					$FullData = "AUTH2 " + $($($Auth2Header + $Auth2Body | ForEach-Object ToString "X2") -join '')
					Serial-Send $FullData
					$Result = $(Serial-Receive)
					If($Result[0] -eq "00000000") {
						$AuthOK = $True
						Write-Host "AUTH2 OK." -ForegroundColor Yellow
						Write-Host "`nAuth successful!" -ForegroundColor Green
						Return
					} Else {
						Write-Host "Error: AUTH2 failed!" -ForegroundColor Red
					}
				} Else {
					Write-Host "Error: AUTH1 response body invalid!" -ForegroundColor Red
				}
			} Else {
				Write-Host "Error: AUTH1 response header invalid!" -ForegroundColor Red
			}
		} Else {
			Write-Host "Error: AUTH1 response invalid!" -ForegroundColor Red
		}
	} Else {
		Write-Host "Sending scopen..."
		Serial-Send "scopen"
		$Result = $(Serial-Receive)

		If($Result -like "*SC_READY*") {
			Write-Host "scopen OK." -ForegroundColor Yellow
			Write-Host "Sending AUTH1..."
			Serial-Send "10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
			$Result = $(Serial-Receive).Replace("`r`n", "").Split("`n")[1]
			# Check if response length is 128
			If($Result.Length -eq 128) {
				Write-Host "AUTH1 OK." -ForegroundColor Yellow
				$BinResult = [byte[]] -split ($Result -replace '..', '0x$& ')
				# Check if the response header is an AUTH1 response header
				If(!(Compare-Object $BinResult[0..15] $Auth1R_Header)) {
					# Decrypt the data
					$Data = Syscon-Decrypt $SC2TB $Zero $BinResult
					# Check if the decrypted data is correct
					If(!(Compare-Object $Data[8..15] $Zero[8..15]) -and !(Compare-Object $Data[16..31] $Value) -and !(Compare-Object $Data[32..47] $Zero)) {
						# Reconstruct the data, encrypt and send
						[byte[]]$NewData = @()
						$NewData += $Data[8..15]
						$NewData += $Data[0..7]
						$NewData += $Zero
						$NewData += $Zero

						$Auth2Body = Syscon-Encrypt $TB2SC $Zero $NewData
						
						Write-Host "Sending AUTH2..."
						$FullData = $($Auth2Header + $Auth2Body | ForEach-Object ToString "X2") -join ''
						Serial-Send $FullData
						$Result = $(Serial-Receive)
						If($Result -like "*SC_SUCCESS*") {
							$AuthOK = $True
							Write-Host "AUTH2 OK." -ForegroundColor Yellow
							Write-Host "Auth successful!" -ForegroundColor Green
							Return
						} Else {
							Write-Host "Error: AUTH2 failed!" -ForegroundColor Red
						}
					} Else {
						Write-Host "Error: AUTH1 response body invalid!" -ForegroundColor Red
					}
				} Else {
					Write-Host "Error: AUTH1 response header invalid!" -ForegroundColor Red
				}
			} Else {
				Write-Host "Error: AUTH1 response invalid!" -ForegroundColor Red
			}
		} Else {
			Write-Host "Error: scopen response invalid!" -ForegroundColor Red
		}
	}
}

# -----------------------------------------------------------------------------------------------------------------------------

Write-Host "`nPS3 Syscon UART script" -ForegroundColor Yellow
Write-Host "https://github.com/db260179/ps3syscon" -ForegroundColor Yellow
Write-Host "PowerShell version by redcyclone`n`n" -ForegroundColor Yellow

Write-Host "Trying to communicate with the Syscon..."

# Communication check
If($Type -eq "CXRF") {
	# Get rid of garbage in the buffer and wait for the prompt
	Serial-Send ""
	Serial-Receive | Out-Null
	$Response = ""
	$Tries = 0
	While(!($Response -like "*[[mullion]]$ ") -and ($Tries -ne 10)) {
		$Tries++
		Serial-Send ""
		$Response = Serial-Receive
	} 
	If($Tries -eq 10) {
		Write-Host "`nError: Couldn't get a good response from the Syscon!`n" -ForegroundColor Red
		$Port.Close()
		$Port.Dispose()
		Exit
	}
	Write-Host "`nCommunication OK!" -ForegroundColor Green
	Write-Host $Response -NoNewline
} Else {
	Serial-Send ""
	Serial-Receive | Out-Null
	# If data is received...
	Write-Host "`nCommunication OK!" -ForegroundColor Green
}

# Main session
$Session = $True
while($Session -eq $True) {
	If(($Type -eq "CXR") -or ($Type -eq "SW")) {
		$Cmd = Read-Host ">$"
	} Else {
		# CXRF has it's own prompt ([mullion]$ ) (most of the time...)
		$Cmd = Read-Host
	}

	If($Cmd -eq "auth") {
		If($AuthOK -eq $False) {
			If(($Type -eq "CXR") -or ($Type -eq "SW")) {
				Serial-Send "EEP GET 3961 01"
				$Result = Serial-Receive
				If($Result.Split(" ")[0] -eq "00000000") {
					Write-Host "A previous Syscon session was already authenticated." -ForegroundColor Yellow
					Write-Host "You can use privileged commands normally." -ForegroundColor Yellow
				} Else {
					# Begin authentication
					Syscon-Auth
				}
			} Else {
				# Begin authentication
				Syscon-Auth
			}
			
			# Get rid of messages
			Serial-Send ""
			Serial-Receive | Out-Null
			If($Type -eq "CXRF") {
				# Get prompt back
				Serial-Send ""
				Write-Host $(Serial-Receive) -NoNewline
			}
		} Else {
			Write-Host "Error: You are already authenticated!" -ForegroundColor Red
		}			
	} ElseIf($Cmd -eq "exit") {
		$Session = $False
	} Else {
		Serial-Send $Cmd
		Write-Host $(Serial-Receive) -NoNewline
	}
}

# End
$Port.Close()
$Port.Dispose()