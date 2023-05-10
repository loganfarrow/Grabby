#Grabby, the better text sniper for windows
#Authored By Logan Farrow and Nicholas Mayer-Rupert, 2023

#Current Bugs:
#History rolling needs to also manage the history textbox
#address how Screenshot can access attributes of App even though it is the parent.

from Screenshot import Screenshot
from screeninfo import get_monitors
import customtkinter
import os
from PIL import Image
import numpy as np
import ctypes
import tkinter as tk


class App(customtkinter.CTk, Screenshot):
    def __init__(self):
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
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")




        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        #self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        #self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="Capture Text", text_color=("gray10", "gray90"),width=100, height=50,command=self.capture_text_button)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=145)
        



        #create the history frame 
        self.history_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        #allow the history frame to expand columns and rows with widgets when the frame is resized
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)



        #create our clear history button and make it stay centered in the top of the screen
        self.history_frame_clear_button = customtkinter.CTkButton(self.history_frame, text="Clear History", text_color=("gray10", "gray90"),width=100, height=25,command=self.clearhistory)
        self.history_frame_clear_button.grid(row=0, column=0, padx=20, pady=10, sticky="n")
        

        #create a history textbox and have it grow with GUI resizing
        self.history_textbox = customtkinter.CTkTextbox(self.history_frame, width=435, height=280)
        self.history_textbox.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        







        # create third frame
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")


        
    

    def capture_text_button(self):
        #get the screenshots for each monitor as a list
        images = self.grab_screenshots()

        for idx, screen in enumerate(get_monitors()):
            window = self.create_image_window(screen, images[idx], idx)
            self.windows.append(window)
        
        
        
        
        


      

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

