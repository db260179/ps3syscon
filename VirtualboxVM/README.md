# VirtualboxVM Guide

## VM requirements

* Virtualbox 6.x, 7.x - Windows or Linux - [Virtualbox website download](https://www.virtualbox.org/wiki/Downloads)
* Virtualbox Extension pack required for USB access to the serial lead

Once virtualbox is installed, import the ova file as an appliance - login/ssh/http details are in the description of the import ova


## VM features

* SSh server running on port 2222 on host - port 22 inside vm
* Web server (nginx) running on port 8080 on host - port 80 inside vm
* Helpful files in home folder and /var/www/html - Firmware/Flash chip checker tool/PS3 Pkgs etc
* Ready to go python requirements and in sync git folder - ~/ps3syscon

## Setup connecting serial lead on host passthrough to VM

In Virtualbox goto the settings page of the 'PS3-SYSCON' VM and click on the USB - [VirtualboxVM/USB-Settings-Serial-Example](/VirtualboxVM/images/USB-serial-settings.png)

Add a filter to the serial lead you have connected to the host PC -> PS3 - The above image example is the serial lead i've filtered.

This will then expose the serial lead to the vm so you can run the helper bash script found in - [Linux/ps3_syscon.sh](/Linux/ps3_syscon.sh)

## Helpful commands from the terminal(V1.1.1 VM image onwards)

docs - Runs markup reader program to view the supplied readmes in this repository

syscon - Bash script to run the python scripts to talk to the syscon and dump/patch the syscon itself
