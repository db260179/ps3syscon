# ABOUT
This program is an edited version the uart_script.py by db260179. This program is a GUI based application to help newcomers easily diagnose your ps3 without needing any knowledge on how to use Python. With this, there is no need to install Python for this to work since it is a compiled application. 
If you need help with installing and running the program. Please use either the youtube link below or SysconReader_Guide.pdf.

# FEATURES
- Simple selection of COM port ranging from 0 - 256
- Simple selection of syscon CXR or SW
- Easy execution of all 20 codes with a simple click of a button
- Feature to execute custom commands from GUI.

# HOW TO INSTALL
1. Download SysconReader_Installer: <a href="https://drive.google.com/file/d/1INFEK7h2oCDDCavw-THuS3aIaYm5p9kG/view</a>
2. Run setup and choose install directory
Thats it. Now to follow instructions below.

# INSTRUCTIONS 
									
1. Find COM port of TTL adapter via Device Manager
2. Open SysconReader.exe
3. Select COM port
4. Select Syscom Variant
5. Press Start
6. Plug adapter in and turn PS3 stanby power on
7. Click "Auth" button to gain authorisation
   - Authorisation may not work first time
   - Common errors may include the following:
   - "Program Error": This means the program recieved no response from Syscon
   - "Auth1 response invalid": This means authorisation failed
   - Continue to next step when program says "Auth Successful"
8. Press "Get Error Codes" Button
   - This may take a while
   - Program will display current process out of 20
   - Inbetween grabbing codes the program may show as "Not Responding" but the program is still working
   - An Error code may take longer to grab if Syscon is unable to complete request.
9. The program will automatically open a text file with the Error codes displayed
10. Done

# COMPATABILITY
									 
This will only work on Windows 10.

Python does not need to be install on computer

# TROUBLESHOOTING 
									
If "Unicode Error" is displayed, you will need to close program and reopen
If Dialog box pops up saying "Fetal error" you will need to reopen the program
If "Program Error" is displayed more than 5 times in a row, you need to do the following steps:
1. Close Program
2. Go to Task Manager
3. Locate uart_script.exe and end task
4. Restart Program

# CREDITS
											
Original Creators: We can thank guys like 'Major' and 'zecoxao' 
for making this possible in the first place. 
We are just running their script. as well as db260179  
GUI Creator: Callum Duddle, Postal_Dude_










