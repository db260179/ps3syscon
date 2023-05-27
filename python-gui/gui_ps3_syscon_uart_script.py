from binascii import unhexlify as uhx
from Cryptodome.Cipher import AES # Requires pycryptodomex module
import os
import string
import sys
import signal
import argparse
import time
import serial.tools.list_ports
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class PS3UART(object):
    def __init__(self, port, sc_type, serial_speed):
        try:
            import serial
        except ImportError:
            messagebox.showerror("Error", "The pyserial module is required. You can install it with 'pip install pyserial'")
            sys.exit(1)

        self.port = port
        self.sc_type = sc_type
        self.serial_speed = serial_speed
        self.ser = serial.Serial()

        self.sc2tb = uhx('71f03f184c01c5ebc3f6a22a42ba9525')  # Syscon to TestBench Key    (0x130 xor 0x4578)
        self.tb2sc = uhx('907e730f4d4e0a0b7b75f030eb1d9d36')  # TestBench to Syscon Key    (0x130 xor 0x4588)
        self.value = uhx('3350BD7820345C29056A223BA220B323')  # 0x45B8
        self.zero  = uhx('00000000000000000000000000000000')

        self.auth1r_header = uhx('10100000FFFFFFFF0000000000000000')
        self.auth2_header  = uhx('10010000000000000000000000000000')

        self.ser.port = port
        if serial_speed == '57600':
            self.ser.baudrate = 57600
        elif serial_speed == '115200':
            self.ser.baudrate = 115200
        else:
            assert False
        self.type = sc_type
        self.ser.timeout = 0.1
        self.ser.open()
        assert self.ser.isOpen()
        self.ser.flush()

    def aes_decrypt_cbc(self, key, iv, data):
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(data)
            return decrypted_data

    def aes_encrypt_cbc(self, key, iv, data):
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_data = cipher.encrypt(data)
            return encrypted_data

    def __del__(self):
        self.ser.close()

    def send(self, data):
        self.ser.write(data.encode('ascii'))

    def receive(self):
        return self.ser.read(self.ser.inWaiting())

    def command(self, com, wait=1, verbose=False):
        if(verbose):
            print('Command: ' + com)

        if(self.type == 'CXR'):
            length = len(com)
            checksum = sum(bytearray(com, 'ascii')) % 0x100
            if(length <= 10):
                self.send('C:{:02X}:{}\r\n'.format(checksum, com))
            else:
                j = 10
                self.send('C:{:02X}:{}'.format(checksum, com[0:j]))
                for i in range(length - j, 15, -15):
                    self.send(com[j:j+15])
                    j += 15
                self.send(com[j:] + '\r\n')
        elif(self.type == 'SW'):
            length = len(com)
            if(length >= 0x40):
                if(self.command('SETCMDLONG FF FF')[0] != 0):
                    return (0xFFFFFFFF, ['Setcmdlong'])
            checksum = sum(bytearray(com, 'ascii')) % 0x100
            self.send('{}:{:02X}\r\n'.format(com, checksum))
        else:
            self.send(com + '\r\n')

        time.sleep(wait)
        answer = self.receive().decode('ascii', 'ignore').strip()
        if(verbose):
            print('Answer: ' + answer)

        if(self.type == 'CXR'):
            answer = answer.split(':')
            if(len(answer) != 3):
                return (0xFFFFFFFF, ['Answer length'])
            checksum = sum(bytearray(answer[2], 'ascii')) % 0x100
            if(answer[0] != 'R' and answer[0] != 'E'):
                return (0xFFFFFFFF, ['Magic'])
            if(answer[1] != '{:02X}'.format(checksum)):
                return (0xFFFFFFFF, ['Checksum'])
            data = answer[2].split(' ')
            if(answer[0] == 'R' and len(data) < 2 or answer[0] == 'E' and len(data) != 2):
                return (0xFFFFFFFF, ['Data length'])
            if(data[0] != 'OK' or len(data) < 2):
                return (int(data[1], 16), [])
            else:
                return (int(data[1], 16), data[2:])
        elif(self.type == 'SW'):
            answer = answer.split('\n')
            for i in range(0, len(answer)):
                answer[i] = answer[i].replace('\n', '').rsplit(':', 1)
                if(len(answer[i]) != 2):
                    return (0xFFFFFFFF, ['Answer length'])
                checksum = sum(bytearray(answer[i][0], 'ascii')) % 0x100
                if(answer[i][1] != '{:02X}'.format(checksum)):
                    return (0xFFFFFFFF, ['Checksum'])
                answer[i][0] += '\n'
            ret = answer[-1][0].replace('\n', '').split(' ')
            if(len(ret) < 2 or len(ret[1]) != 8 and not all(c in string.hexdigits for c in ret[1])):
                return (0, [x[0] for x in answer])
            elif(len(answer) == 1):
                return (int(ret[1], 16), ret[2:])
            else:
                return (int(ret[1], 16), [x[0] for x in answer[:-1]])
        else:
            return (0, [answer])

    def auth(self):
        if(self.type == 'CXR' or self.type == 'SW'):
            auth1r = self.command('AUTH1 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
            if(auth1r[0] == 0 and auth1r[1] != []):
                auth1r = uhx(auth1r[1][0])
                if(auth1r[0:0x10] == self.auth1r_header):
                    data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[0x10:0x40])
                    if(data[0x8:0x10] == self.zero[0x0:0x8] and data[0x10:0x20] == self.value and data[0x20:0x30] == self.zero):
                        new_data = data[0x8:0x10] + data[0x0:0x8] + self.zero + self.zero
                        auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                        auth2r = self.command('AUTH2 ' + ''.join('{:02X}'.format(c) for c in bytearray(self.auth2_header + auth2_body)))
                        if(auth2r[0] == 0):
                            return 'Auth successful'
                        else:
                            return 'Auth failed'
                    else:
                        return 'Auth1 response body invalid'
                else:
                    return 'Auth1 response header invalid'
            else:
                return 'Auth1 response invalid'
        else:
            scopen = self.command('scopen')
            if('SC_READY' in scopen[1][0]):
                auth1r = self.command('10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
                auth1r = auth1r[1][0].split('\r')[1][1:]
                if(len(auth1r) == 128):
                    auth1r = uhx(auth1r)
                    if(auth1r[0:0x10] == self.auth1r_header):
                        data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[0x10:0x40])
                        if(data[0x8:0x10] == self.zero[0x0:0x8] and data[0x10:0x20] == self.value and data[0x20:0x30] == self.zero):
                            new_data = data[0x8:0x10] + data[0x0:0x8] + self.zero + self.zero
                            auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                            auth2r = self.command(''.join('{:02X}'.format(c) for c in bytearray(self.auth2_header + auth2_body)))
                            if('SC_SUCCESS' in auth2r[1][0]):
                                return 'Auth successful'
                            else:
                                return 'Auth failed'
                        else:
                            return 'Auth1 response body invalid'
                    else:
                        return 'Auth1 response header invalid'
                else:
                    return 'Auth1 response invalid'
            else:
                return 'scopen response invalid'

def main():
    def handle_command():
        port = port_combobox.get()  # Retrieve the selected port from the combobox
        command = command_entry.get()
        sc_type = sc_type_combobox.get()
        if not port or not sc_type:
            messagebox.showerror("Error", "Please enter both the serial port and SC type.")
            return
        
        print("Port:", port)  # Debug print
        print("SC Type:", sc_type)  # Debug print
        print ("Command:", command) # Debug command

        if sc_type == "CXR":
            serial_speed = "57600"
        else:
            serial_speed = "115200"

        ps3 = PS3UART(port, sc_type, serial_speed)
        command = command_entry.get()
        ret = ps3.command(command)
        if ret[0] == 0xFFFFFFFF:
            messagebox.showerror("Error", "Command execution failed: {}".format(ret[1][0]))
            return
        if(sc_type == 'CXR'):
            output = '{:08X}'.format(ret[0]) + ' ' + ' '.join(ret[1])
        elif(sc_type == 'SW'):
            if(len(ret[1]) > 0 and '\n' not in ret[1][0]):
                output = '{:08X}'.format(ret[0]) + ' ' + ' '.join(ret[1])
            else:
                output = '{:08X}'.format(ret[0]) + '\n' + ''.join(ret[1])
        else:
            output = ret[1][0]
        output_text.insert(tk.END, output + '\n')

    def handle_auth():
        port = port_combobox.get()  # Retrieve the selected port from the combobox
        sc_type = sc_type_combobox.get()
        if not port or not sc_type:
            messagebox.showerror("Error", "Please enter the serial port, SC type.")
            return

        if sc_type == "CXR":
            serial_speed = "57600"
        else:
            serial_speed = "115200"

        ps3 = PS3UART(port, sc_type, serial_speed)
        result = ps3.auth()
        messagebox.showinfo("Authentication Result", result)

    def open_error_logs_lookup():
        url = "https://www.psdevwiki.com/ps3/Syscon_Error_Codes"  # psdevwiki ps3
        webbrowser.open(url)

    def show_help():
        commands = [
            "External mode:",
            "EEP GET (get EEPROM address)",
            "EEP SET (set EEPROM address value)",
            "ERRLOG GET 00 (get errorlog from code 0 - repeat until 1F)",
            "",
            "Internal mode:",
            "eepcsum (check EEPROM checksum)",
            "errlog (get errlog)",
            "clearerrlog (clear errorlog)",
            "r (read from eeprom address)",
            "w (write to eeprom address)",
            "fantbl (get/set/getini/setini/gettable/settable)",
            "patchvereep (get patched version)",
            "",
            "Read the PS3-Uart-Guide-V2.pdf for further information"
        ]

        # Create the helper window
        helper_window = tk.Toplevel()
        helper_window.title("Available Commands")

        # Create a text widget to display the commands
        commands_text = tk.Text(helper_window, height=len(commands), width=60)
        commands_text.pack(fill=tk.BOTH, expand=True)

        # Insert the commands into the text widget
        for command in commands:
            commands_text.insert(tk.END, command + "\n")

        # Disable text editing
        commands_text.configure(state=tk.DISABLED)

        # Start the Tkinter event loop for the helper window
        helper_window.mainloop()
        
    def refresh_ports():
        ports = []
        for port in serial.tools.list_ports.comports():
            if "Serial" in port.description:
                ports.append(port.device)
        port_combobox['values'] = ports

    def handle_syscon_serial_output():
        serial_port = port_combobox.get()  # Retrieve the selected port from the combobox
        sc_type = sc_type_combobox.get()
        if not serial_port or not sc_type:
            messagebox.showerror("Error", "Please enter the serial port and SC type.")
            return

        if sc_type == "CXR":
            baud_rate = "57600"
        else:
            baud_rate = "115200"

        # Path to gui_diag_serial.py
        script_path = "gui_diag_serial.py"

        # Determine the platform (Windows or Linux) and set the appropriate command
        if sys.platform.startswith('win'):
            command = ["python", script_path, serial_port, baud_rate]
        else:
            command = ["python3", script_path, serial_port, baud_rate]

        # Run the gui_diag_serial.py script using subprocess
        subprocess.run(command)

    # Create the main window
    window = tk.Tk()
    window.title("PS3UART GUI")

    # Create input frame
    input_frame = tk.Frame(window)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    # Create port label and entry
    port_label = tk.Label(input_frame, text="Serial Port: (Examples: /dev/ttyUSB0 or COM1)")
    port_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    port_combobox = ttk.Combobox(input_frame, values=serial.tools.list_ports.comports())
    port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    refresh_button = tk.Button(input_frame, text="Refresh", command=refresh_ports)
    refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    # Get available serial ports
    available_ports = [port.device for port in serial.tools.list_ports.comports()]

    # Create port dropdown list
    port_combobox = ttk.Combobox(input_frame, values=available_ports)
    port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Create SC type label and combobox
    sc_type_label = tk.Label(input_frame, text="SC Type: (Syscon type)")
    sc_type_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    sc_type_combobox = ttk.Combobox(input_frame, values=["CXR", "CXRF", "SW"])
    sc_type_combobox.set("CXR")  # Set the default value to "CXR"
    sc_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Create command label and entry
    command_label = tk.Label(window, text="Command:")
    command_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    command_entry = tk.Entry(window)
    command_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

    # Create output text widget
    output_text = tk.Text(window, height=10, width=60)
    output_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Create buttons
    input_button = tk.Button(window, text="Send Command", command=handle_command)
    input_button.grid(row=3, column=0, padx=10, pady=5, sticky="we")

    auth_button = tk.Button(window, text="Auth", command=handle_auth)
    auth_button.grid(row=3, column=1, padx=10, pady=5, sticky="we")

    help_button = tk.Button(window, text="Help", command=show_help)
    help_button.grid(row=4, column=0, padx=10, pady=5, sticky="we")

    error_logs_button = tk.Button(window, text="Psdevwiki - Error logs", command=open_error_logs_lookup)
    error_logs_button.grid(row=4, column=1, padx=10, pady=5, sticky="we")

    # Create Syscon Serial Output button
    syscon_serial_output_button = tk.Button(window, text="Diagnose Syscon Serial Output", command=handle_syscon_serial_output)
    syscon_serial_output_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Configure grid weights to make the widgets scale with the window
    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(1, weight=1)

    # Start the Tkinter event loop
    window.mainloop()

# Call main function
if __name__ == '__main__':
    main()