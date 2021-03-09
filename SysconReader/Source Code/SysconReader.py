import os
import time
from Tkinter import *

comfirm_exit_file = open ("confirm_exit.txt", "w")
comfirm_exit_file.write("false")
comfirm_exit_file.close()

first_window = Tk()
first_window.title("Select Port Options")
first_window.geometry("450x250")
first_window.resizable(False, False)


title_label = Label(first_window, text="Enter Details Below", anchor="center")
title_label.config(font=("Times New Roman", 22))
title_label.place(relx=0.22, rely=0.1)

sub_label = Label(first_window, text="Select COM port of TTL adaptor", anchor="center")
sub_label.config(font=("Times New Roman", 12))
sub_label.place(relx=0.25, rely=0.25)

sub2_label = Label(first_window, text="Pick either CXR or SW depending on console", anchor="center")
sub2_label.config(font=("Times New Roman", 12))
sub2_label.place(relx=0.15, rely=0.35)

#generate com ports

options = []
for i in range(257):
    temp_i = str(i)
    current = "COM" + temp_i
    options.append(current)
print (options)

def start():
    print ("Noice!")
    start_options = []
    start_options = str(var.get()) + " " + str(var2.get())
    print (start_options)

    #config
    config_file = open ("config.txt", "w")
    config_file.write(start_options)
    config_file.close()

    
    first_window.destroy()
    os.startfile("uart_script.exe")
    

def help_():
    os.startfile("readme.txt")


options_sys = ["CXR", "SW"]


var = StringVar(first_window)
var.set(options[4])
com_options = OptionMenu(first_window, var, *options)
com_options.config(font=("Times New Roman", 18), width=8)
com_options.place(relx=0.12, rely=0.5)

var2 = StringVar(first_window)
var2.set(options_sys[0])
sys_options = OptionMenu(first_window, var2, *options_sys)
sys_options.config(font=("Times New Roman", 18), width=8)
sys_options.place(relx=0.58, rely=0.5)


start_button = Button(first_window, text="Start", command=start)
start_button.config(font=("Times New Roman", 18), anchor="center", width=10)
start_button.place(relx=0.35, rely=0.75)

help_button = Button(first_window, text="?", command=help_)
help_button.config(font=("Times New Roman", 12), anchor="center", width=3)
help_button.place(relx=0.01, rely=0.85)


def exit_app():
    first_window.destroy()
    comfirm_exit_file = open ("confirm_exit.txt", "w")
    comfirm_exit_file.write("true")
    comfirm_exit_file.close()
    exit()

first_window.protocol("WM_DELETE_WINDOW", exit_app)

first_window.mainloop()

print ("Starting Script")



#main

comfirm_exit_file = open ("confirm_exit.txt", "r")
check_stat = comfirm_exit_file.read()
check_stat = str(check_stat)

if check_stat == "true":
    pass

else:

    auth_success = False


    first_window = Tk()
    first_window.title("Syscon Error Reader")
    first_window.geometry("450x250")
    first_window.resizable(False, False)


    title_label = Label(first_window, text="Instructions", anchor="center")
    title_label.config(font=("Times New Roman", 22))
    title_label.place(relx=0.35, rely=0.05)


    sub2_label = Label(first_window, text="1. Start Authorisation", anchor="center")
    sub2_label.config(font=("Times New Roman", 12))
    sub2_label.place(relx=0.35, rely=0.20)

    sub22_label = Label(first_window, text="2. Grab Syscon Errors Codes. Simple", anchor="center")
    sub22_label.config(font=("Times New Roman", 12))
    sub22_label.place(relx=0.25, rely=0.30)


    def start_auth():

        auth_file = open ("auth_output.txt", "w")
        auth_file.write("none")
        auth_file.close()

        time.sleep(1)

        
        command_file = open("command.txt", "w")
        command_file.write("auth")
        command_file.close()

        
        count = 0

        command_recieved = False
        while not command_recieved:
            auth_file = open ("auth_output.txt", "r")
            get_command = auth_file.read()
            get_command = str(get_command)
            auth_file.close()

            time.sleep(0.03)

            count += 1


            if count >= 200:
                print ("Program Error")
                sub_label.config(text= "Program Error", font=("Times New Roman", 15), fg="red")
                sub_label.place(relx=0.44, rely=0.49)
                sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")
                command_recieved = True

            print (get_command)

            if get_command == "none" or get_command == "":
                pass
            else:
                print ("output:", get_command)
                if get_command == "Auth successful":
                    print ("yes noice")
                    sub_label.config(text= "Auth Successful", font=("Times New Roman", 15), fg="green")
                    sub_label.place(relx=0.44, rely=0.49)
                    auth_success = True
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="active")
                elif get_command == "Auth failed":
                    sub_label.config(text= "Auth Failed", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")
                elif get_command == "Auth1 response invalid":
                    sub_label.config(text= "Auth1 response invalid", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")
                elif get_command == "Auth1 response body invalid":
                    sub_label.config(text= "Auth1 response body invalid", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")
                elif get_command == "Auth1 response header invalid":
                    sub_label.config(text= "Auth1 response header invalid", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")
                elif get_command == "scopen response invalid":
                    sub_label.config(text= "scopen response invalid", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)
                    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="disabled")

                elif get_command == "unicode error":
                    sub_label.config(text= "Unicode Error", font=("Times New Roman", 15), fg="red")
                    sub_label.place(relx=0.44, rely=0.49)

                    print ("reboot program...")
                    os.startfile("uart_script.exe")



                


                
                command_recieved = True

        print ("done auth") #debug
            

    def on_close():
        command_file = open("command.txt", "w")
        command_file.write("exit")
        command_file.close()
        first_window.destroy()


    def start_auth_print():
        sub_label.config(text= "Starting Auth", font=("Times New Roman", 15), fg="black")
        sub_label.place(relx=0.44, rely=0.49)
        first_window.after(1000, start_auth)


    start_button = Button(first_window, text="Auth", command=start_auth_print)
    start_button.config(font=("Times New Roman", 18), anchor="center", width=10)
    start_button.place(relx=0.10, rely=0.45)


    sub_label = Label(first_window, text="Waiting For Sys Auth", anchor="center")
    sub_label.config(font=("Times New Roman", 15), fg="darkgrey")
    sub_label.place(relx=0.44, rely=0.49)

    def get_codes():
        print ("noice")


        total_codes = []

        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        sys_label.config(text="Grabbing (1/20")
        first_window.update_idletasks()
        first_window.update()


        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        
        command_file = open("command.txt", "w")
        command_file.write("ERRLOG GET 00")
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)

            time.sleep(0.03)
            print ("none")

            count += 1

            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 00")
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 00")
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num = 1


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks() 
        first_window.update()

        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write("ERRLOG GET 01")
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 01")
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 01")
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        num = 1

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update() 
        

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 0" + str(num) #get 09
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True



        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        




        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write("ERRLOG GET 10")
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 10")
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write("ERRLOG GET 10")
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        num = 0


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

            

        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True

        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        

        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        count_num += 1
        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        print_text = "Grabbing (" + str(count_num) + "/20)"
        sys_label.config(text=print_text)
        first_window.update_idletasks()
        first_window.update()

        
        num += 1
        current_code_file_command = "ERRLOG GET 1" + str(num)
        code_file = open ("current_code.txt", "w")
        code_file.write("none")
        code_file.close()
        time.sleep(3)
        command_file = open("command.txt", "w")
        command_file.write(current_code_file_command)
        command_file.close()
        count = 0
        command_recieved = False
        while not command_recieved:
            code_file = open ("current_code.txt", "r")
            current_code = code_file.read()
            current_code = str(current_code)
            time.sleep(0.03)
            print ("none")
            count += 1
            if count >= 200:
                print ("Error")
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            if current_code == "none" or current_code == "":
                pass
            elif current_code == "F0000001 " or current_code == "FFFFFFFF " or current_code == "F0000003" or "F0000003" in current_code:
                time.sleep(3)
                code_file = open ("current_code.txt", "w")
                code_file.write("none")
                code_file.close()
                command_file = open("command.txt", "w")
                command_file.write(current_code_file_command)
                command_file.close()
            else:
                print (current_code)
                total_codes.append(current_code)
                command_recieved = True


        



            


        


        

     

        

        
        

        
        






        







        print ("done")
        print ("========================")
        for items in total_codes:
            print (items)
        print ("========================")

        


        sys_label.config(text="")
        first_window.update_idletasks()
        first_window.update_idletasks()
        first_window.update_idletasks()
        sys_label.config(text="Complete")
        first_window.update_idletasks()



        print ("Writing Text File")

        cur_err_num = 0
        log_file = open ("errorcodes.txt", "w")
        log_file.write("===================================\n")
        for items in total_codes:
            if cur_err_num < 10:
                new_line = "ERR 0" + str(cur_err_num) + ": " + items + "\n"
            else:
                new_line = "ERR " + str(cur_err_num) + ": " + items + "\n"
            log_file.write(new_line)
            cur_err_num += 1
        log_file.write("===================================\n")
        log_file.close()

        
        time.sleep(2)
        print ("Loading Text File")
        os.startfile("errorcodes.txt")

            

        

    def get_codes_print():
        sys_label.config(text="Starting...")
        first_window.after(1000, get_codes)




    sys_button = Button(first_window, text="Get Error Codes", command=get_codes_print)
    sys_button.config(font=("Times New Roman", 18), anchor="center", width=15, state="active") #debug
    sys_button.place(relx=0.10, rely=0.70)

    sys_label = Label(first_window, text="__blank__", anchor="center")
    sys_label.config(font=("Times New Roman", 15), fg="black")
    sys_label.place(relx=0.59, rely=0.74)
























    version_label = Label(first_window, text="Version: 0.4", anchor="center")
    version_label.config(font=("Times New Roman", 10), fg="black")
    version_label.place(relx=0.01, rely=0.92)

    first_window.protocol("WM_DELETE_WINDOW", on_close)


    def refresh():
        a = "a"


    first_window.after(5000,refresh)
    first_window.mainloop()






    #time.sleep(7)
    #command_file = open("command.txt", "w")
    #command_file.write("auth")
    #command_file.close()
