#!/usr/bin/python3
import argparse
import os
import sys

def main(serial_port, baud_rate, log_file):

    # Loop to read data from serial port and write to screen and log file
    print('Press Ctrl+C to exit')
    try:
        # Serial port configuration
        ser = serial.Serial(serial_port, baud_rate, timeout=2)

        while True:
            # Read data from serial port
            data = ser.readline()

            # Decode data from bytes to string
            data_str = data.decode('utf-8')

            # Print data to screen
            print(data_str)

            # Write data to log file
            if log_file is not None:
                log_file.write(data_str)
                log_file.flush()

    except KeyboardInterrupt:
        print("Exiting script...")
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        # Close serial port and log file
        ser.close()
        if log_file is not None:
            log_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Diagnose the Syscon by reading data from a serial port and output to screen and log file.')
    parser.add_argument('serial_port', help='the serial port to connect to i.e. /dev/ttyUSB0')
    parser.add_argument('baud_rate', type=int, help='the baud rate to use i.e. CXR=57600, CXRF=115200')
    parser.add_argument('-l', '--logfile', default=None, help='the log file to write to (default: None)')

    args = parser.parse_args()

    try:
        # Check if required Python modules are installed
        import serial
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Serial port configuration
    try:
        ser = serial.Serial(args.serial_port, args.baud_rate, timeout=1)
    except serial.serialutil.SerialException as e:
        print('Error: Unable to connect to serial port: {}'.format(e))
        sys.exit(1)

    # Log file configuration
        if args.logfile is not None:
            try:
                log_file = open(args.logfile, 'a')
            except IOError as e:
                print('Error: Unable to open log file: {}'.format(e))
                sys.exit(1)
        else:
            log_file = None

    # Call main function with parsed arguments
    main(args.serial_port, args.baud_rate, args.logfile)