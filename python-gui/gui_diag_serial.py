#!/usr/bin/python3
import argparse
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import serial
import serial.tools.list_ports
import threading

class SerialMonitorGUI:
    def __init__(self, serial_port, baud_rate, log_file=None):
        self.root = tk.Tk()
        self.root.title("Serial Monitor")
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        self.serial_ports = []
        self.detect_serial_ports()

        self.serial_port_label = tk.Label(self.root, text="Serial Port:")
        self.serial_port_label.pack()
        self.serial_port_combobox = ttk.Combobox(self.root, values=self.serial_ports)
        self.serial_port_combobox.pack()
        self.serial_port_combobox.set(serial_port)

        self.baud_rate_label = tk.Label(self.root, text="Baud Rate:")
        self.baud_rate_label.pack()
        self.baud_rate_combobox = ttk.Combobox(self.root, values=["57600", "115200"])
        self.baud_rate_combobox.pack()
        self.baud_rate_combobox.set(str(baud_rate))

        self.log_file_label = tk.Label(self.root, text="Log File (optional):")
        self.log_file_label.pack()
        self.log_file_entry = tk.Entry(self.root)
        self.log_file_entry.pack()
        if log_file is not None:
           self.log_file_entry.insert(tk.END, log_file)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack()

        self.output_text = tk.Text(self.root)
        self.output_text.pack()

        self.is_monitoring = False
        self.ser = None
        self.log_file_handle = None

    def detect_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        self.serial_ports = [port.device for port in ports]

    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_monitoring()
            self.root.destroy()

    def start_monitoring(self):
        if self.is_monitoring:
            return

        serial_port = self.serial_port_combobox.get()
        baud_rate = int(self.baud_rate_combobox.get())
        log_file = self.log_file_entry.get()

        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))
            return

        if log_file:
            try:
                self.log_file_handle = open(log_file, 'a')
            except IOError as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            self.log_file_handle = None

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.serial_port_combobox.configure(state=tk.DISABLED)
        self.baud_rate_combobox.configure(state=tk.DISABLED)
        self.log_file_entry.configure(state=tk.DISABLED)

        self.is_monitoring = True

        # Create a separate thread for serial communication
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.start()

    def stop_monitoring(self):
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.ser is not None:
            self.ser.close()

        if self.log_file_handle is not None:
            self.log_file_handle.close()

        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.serial_port_combobox.configure(state=tk.NORMAL)
        self.baud_rate_combobox.configure(state=tk.NORMAL)
        self.log_file_entry.configure(state=tk.NORMAL)

    def read_serial(self):
        try:
            while self.is_monitoring:
                if self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting)
                    data_str = data.decode('utf-8', 'backslashreplace')
                    self.root.after(10, self.update_output, data_str)

                    if self.log_file_handle is not None:
                        self.log_file_handle.write(data_str)
                        self.log_file_handle.flush()
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def update_output(self, data_str):
        self.output_text.insert(tk.END, data_str)
        self.output_text.see(tk.END)

def main(serial_port, baud_rate, log_file):
    try:
        gui = SerialMonitorGUI(serial_port, baud_rate, log_file)
        gui.root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Diagnose the Syscon by reading data from a serial port and output to screen and log file.')
    parser.add_argument('serial_port', help='the serial port to connect to i.e. /dev/ttyUSB0')
    parser.add_argument('baud_rate', type=int, help='the baud rate to use i.e. 57600, 115200')
    parser.add_argument('-l', '--logfile', default=None, help='the log file to write to (default: None)', nargs='?')
    args = parser.parse_args()

    main(args.serial_port, args.baud_rate, args.logfile)
