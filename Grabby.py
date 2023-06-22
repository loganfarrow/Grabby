#Grabby, the better text sniper for windows
#Authored By Logan Farrow and Nicholas Mayer-Rupert, 2023

#Current Bugs:
#History rolling needs to also manage the history textbox
#address how Screenshot can access attributes of App even though it is the parent.

from tktooltip import ToolTip
from Screenshot import Screenshot
from screeninfo import get_monitors
import customtkinter
import os
import keyboard
from PIL import Image
import numpy as np
import ctypes
import tkinter as tk
from pystray import MenuItem as item
import pystray
from tkinter import filedialog
import threading
import time








class App(customtkinter.CTk, Screenshot):
    def __init__(self):
        
        self.useGoogleVision = False
        self.useSnippingTool = False
        
        self.isMinimized = False
        
        #credentials for google vision
        self.credentials = None
        
        super().__init__()
        Screenshot.__init__(self)

        self.title("Grabby")
        self.geometry("650x350")
        self.minsize(650, 350)

        # Initialize windows list and x1, y1 variables
        self.windows = []
        self.x1 = None
        self.y1 = None


        #get scaling information for more compatability 
        user32 = ctypes.windll.user32
        screen_dpi = user32.GetDpiForSystem()
        
        #keybind info stores the keybind, addhotkey allows it 
        #to be called using the keybind.AAAAA
        self.keybind_info = 'windows+shift'
        self.t_hotkey_listener = threading.Thread(target=self.run_hotkey_listener,daemon=True)
        self.t_hotkey_listener.start()
        
        ## Calculate the scaling factor
        self.scaling_factor = screen_dpi / 96.0  # 96 DPI is the standard for most displays

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "paperblack.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "paperwhite.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "cog.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "coglight.png")), size=(20, 20))

        # create navigation frame with a button for Home, History, and Settings
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Grabby", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.history_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="History",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.history_button_event)
        self.history_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")
        

        #create the appear mode menu within the nagivation frame
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")




        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)


        #set up the home frame buttons 

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="Capture Text", text_color=("gray10", "gray90"), width=100, height=50, command=self.capture_text_button)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=15, sticky="ew")

        self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="Minimize To Tray", text_color=("gray10", "gray90"), width=100, height=50, command=self.create_sys_tray_icon)
        self.home_frame_button_2.grid(row=2, column=0, padx=20, pady=15,sticky="ew")

        self.home_frame_button_3 = customtkinter.CTkButton(self.home_frame, text="Read From File", text_color=("gray10", "gray90"), width=100, height=50, command=self.read_from_file)
        self.home_frame_button_3.grid(row=1, column=0, padx=20, pady=15,sticky="ew")

        




        #create the history frame 
        self.history_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        

        #allow the history frame to expand columns and rows with widgets when the frame is resized
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)



        #create our clear history button and make it stay centered in the top of the screen
        self.history_frame_clear_button = customtkinter.CTkButton(self.history_frame, text="Clear History", text_color=("gray10", "gray90"),width=100, height=25,command=self.clearhistory)
        self.history_frame_clear_button.grid(row=0, column=0, padx=20, pady=10, sticky="n")
        

        #create a history textbox and have it grow with GUI resizing
        self.history_textbox = customtkinter.CTkTextbox(self.history_frame, width=435, height=280)
        self.history_textbox.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        





        # create settings frame
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        #self.settings_frame.grid_rowconfigure(1, weight=1)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        
        self.text_decoder_label = customtkinter.CTkLabel(self.settings_frame, text="Text Decoder", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.text_decoder_label.grid(row=0, column=0, padx=0, pady=0, sticky="n")

        # create settings button for setting up the text decoder
        self.settings_button1 = customtkinter.CTkSegmentedButton(self.settings_frame,command=self.api_button_handler)
        self.settings_button1.configure(values=["PyTesseract", "Google Vision"])
        self.settings_button1.set("PyTesseract")


        
        self.settings_button1.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        
        self.screenshot_mode = customtkinter.CTkLabel(self.settings_frame, text="Screenshot Mode", font=customtkinter.CTkFont(size=15, weight="bold"),)
        self.screenshot_mode.grid(row=6, column=0, padx=0, pady=0, sticky="n")
        
        self.screenshot_button = customtkinter.CTkSegmentedButton(self.settings_frame,command=self.snipping_handler)
        self.screenshot_button.configure(values=["Built-in Screen Capture", "Snipping Tool"])
        self.screenshot_button.set("Built-in Screen Capture")
        self.screenshot_button.grid(row=8, column=0, padx=20, pady=0, sticky="ew")


        self.select_frame_by_name("home")

        self.text_decoder_label = customtkinter.CTkLabel(self.settings_frame, text="API Credentials Path", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.text_decoder_label.grid(row=10, column=0, padx=0, pady=0, sticky="n")
        
        self.filepath_textbox = customtkinter.CTkTextbox(self.settings_frame, width=435, height=25)
        self.filepath_textbox.grid(row=13, column=0, padx=20, pady=0, sticky='ew')
        self.filepath_textbox.configure(state=tk.DISABLED)

        self.filepath_button = customtkinter.CTkButton(self.settings_frame, text="Select File", text_color=("gray10", "gray90"), width=100, height=25, command=self.open_file_dialog)
        self.filepath_button.grid(row=12, column=0, padx=20, pady=0, sticky="ew")




    def open_file_dialog(self):
        self.filepath_textbox.configure(state=tk.NORMAL)
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

        if file_path:
            self.credentials = file_path
            self.filepath_textbox.insert('1.0', file_path)  # Insert the filepath into the textbox
        self.filepath_textbox.configure(state=tk.DISABLED)






    def api_button_handler(self,value):
        if value == "PyTesseract":
            self.useGoogleVision = False
        else:
            if self.credentials == None:
                self.open_file_dialog()
                
            self.useGoogleVision = True

            
        

    
    def snipping_handler(self,value):
        if value == "Built-in Screen Capture":
            self.useSnippingTool = False
        else:
            self.useSnippingTool = True
                

         

    

    def create_sys_tray_icon(self):
        print("hello")
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images", "hand.ico")
        image = Image.open(image_path)
        print("hello2")
        menu = (item('Show', self.show_from_tray), item('Quit', self.stop_program))
        print("hello3")
        self.icon = pystray.Icon("name", image, "Grabby", menu)
        self.minimize_app()
        
    def show_from_tray(self):
        self.icon.stop()
        self.deiconify()
        self.update()
        self.isMinimized = False


    def stop_program(self):
        self.icon.stop()
        self.quit()
        

    def minimize_app(self):
        print("hello4")
        self.isMinimized = True
        self.withdraw()
        self.icon.run()
        print("hello5")

        

    def run_hotkey_listener(self):
        keyboard.add_hotkey(self.keybind_info, self.hotkey_function)
        keyboard.wait()


    def hotkey_function(self):
        self.capture_text_button()    
        
        
    
  
    def capture_text_button(self):
        if self.isMinimized == False:
            #get the screenshots for each monitor as a list
            images = self.grab_screenshots()
            for idx, screen in enumerate(get_monitors()):
                window = self.create_image_window(screen, images[idx], idx)
                self.windows.append(window)
        else:
            self.show_from_tray()
            time.sleep(1)    
            #get the screenshots for each monitor as a list
            images = self.grab_screenshots()
            for idx, screen in enumerate(get_monitors()):
                window = self.create_image_window(screen, images[idx], idx)
                self.windows.append(window)
            time.sleep(1)    
            self.create_sys_tray_icon()
            print(self.isMinimized)

<<<<<<< HEAD
=======
        for idx, screen in enumerate(get_monitors()):
            window = self.create_image_window(screen, images[idx], idx)
            self.windows.append(window)
    

    def read_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])

        if file_path:  # To ensure a file was selected
            img = Image.open(file_path)

            if(self.useGoogleVision):
                self.google_vision_extract_text(file_path)
            else:
                self.pytesseract_extract_text(img)



>>>>>>> 7d0caa48bad1c349d3b5c474b9102d4a9fbe5a98
        
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.history_button.configure(fg_color=("gray75", "gray25") if name == "history_frame" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings_frame" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "history_frame":
            self.history_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.history_frame.grid_forget()
        if name == "settings_frame":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def history_button_event(self):
        self.select_frame_by_name("history_frame")

    def settings_button_event(self):
        self.select_frame_by_name("settings_frame")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    

    def clearhistory(self):
        self.history = []

        #first set the state to normal so text can be changed, then delete all of the text 
        self.history_textbox.configure(state=tk.NORMAL)
        self.history_textbox.delete("1.0", tk.END)
        self.history_textbox.configure(state=tk.DISABLED)
    
    def historylength(self,num):
        try:
            if num >= 0 and num <= 10:
                self.historysize = num
            else:
                pass
        except ValueError:
            pass
        

        
    
    
    


if __name__ == "__main__":
    app = App()
    app.mainloop()

