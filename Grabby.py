# Grabby, the better text sniper for windows
# Authored By Logan Farrow and Nicholas Mayer-Rupert, 2023
import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter
import keyboard
import pystray
from PIL import Image,ImageGrab
from pystray import MenuItem as item
from screeninfo import get_monitors
from Screenshot import Screenshot
import json


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.screenshot_handler = Screenshot(self)

        #set icon
        icon_path = self.resource_path(os.path.join("images", "logo_icon.ico"))
        self.iconbitmap(icon_path)

        # tracker for OCR type
        self.useGoogleVision = False
        

        # Minimized tracker
        self.isMinimized = False

        # credentials for google vision
        self.credentials = None

        

        self.title("Grabby")
        self.geometry("650x350")
        self.minsize(650, 350)

        # Initialize windows list and x1, y1 variables
        self.windows = []
        self.x1 = None
        self.y1 = None

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = self.resource_path("images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")),
                                                 size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")),
                                                       size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")),
                                                       size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")),
                                                 size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "paperblack.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "paperwhite.png")),
                                                 size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "cog.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "coglight.png")),
                                                     size=(20, 20))

        # create navigation frame with a button for Home, History, and Settings
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="rabby",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))

        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.history_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="History",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w",
                                                      command=self.history_button_event)
        self.history_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.add_user_image, anchor="w",
                                                       command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")

        # create the appear mode menu within the nagivation frame
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["System", "Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        # set up the home frame buttons

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="Capture Text",
                                                           text_color=("gray10", "gray90"), width=100, height=50,
                                                           command=self.capture_text_button)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=15, sticky="ew")

        self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="Minimize to Tray",
                                                           text_color=("gray10", "gray90"), width=100, height=50,
                                                           command=self.create_sys_tray_icon)
        self.home_frame_button_2.grid(row=3, column=0, padx=20, pady=15, sticky="ew")

        self.home_frame_button_3 = customtkinter.CTkButton(self.home_frame, text="Read from File",
                                                           text_color=("gray10", "gray90"), width=100, height=50,
                                                           command=self.read_from_file)
        self.home_frame_button_3.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        self.home_frame_button_4 = customtkinter.CTkButton(self.home_frame, text="Capture from Clipboard",
                                                           text_color=("gray10", "gray90"), width=100, height=50,
                                                           command=self.capture_from_clipboard)
        self.home_frame_button_4.grid(row=2, column=0, padx=20, pady=15, sticky="ew")

        # create the history frame
        self.history_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # allow the history frame to expand columns and rows with widgets when the frame is resized
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)

        # create our clear history button and make it stay centered at the top of the screen
        self.history_frame_clear_button = customtkinter.CTkButton(self.history_frame, text="Clear History",
                                                                  text_color=("gray10", "gray90"), width=100, height=25,
                                                                  command=self.clearhistory)
        self.history_frame_clear_button.grid(row=0, column=0, padx=20, pady=10, sticky="n")

        # create a history textbox and have it grow with GUI resizing
        self.history_textbox = customtkinter.CTkTextbox(self.history_frame, width=435, height=280)
        self.history_textbox.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        # create settings frame
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        # self.settings_frame.grid_rowconfigure(1, weight=1)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.text_decoder_label = customtkinter.CTkLabel(self.settings_frame, text="Text Decoder",
                                                         font=customtkinter.CTkFont(size=15, weight="bold"))
        self.text_decoder_label.grid(row=0, column=0, padx=0, pady=0, sticky="n")

        # create settings button for setting up the text decoder
        self.settings_button1 = customtkinter.CTkSegmentedButton(self.settings_frame, command=self.api_button_handler)
        self.settings_button1.configure(values=["PyTesseract", "Google Vision"])
        self.settings_button1.set("PyTesseract")
        self.settings_button1.grid(row=1, column=0, padx=20, pady=0, sticky="ew")

        # Screenshot Mode button setup
        self.screenshot_mode = customtkinter.CTkLabel(self.settings_frame, text="Custom Capture Clipboard Keybind",
                                                      font=customtkinter.CTkFont(size=15, weight="bold"), )
        self.screenshot_mode.grid(row=17, column=0, padx=0, pady=0, sticky="n")

        self.keybind_button_clipboard = customtkinter.CTkButton(self.settings_frame, text="Record Input - Press Escape to End",
                                                       text_color=("gray10", "gray90"), width=100, height=25,
                                                       command=self.record_keybind_button_hanlder_clipboard)
        self.keybind_button_clipboard.grid(row=18, column=0, padx=20, pady=0, sticky="ew")

        self.keybind_textbox_clipboard = customtkinter.CTkTextbox(self.settings_frame, width=435, height=25)
        self.keybind_textbox_clipboard.grid(row=19, column=0, padx=20, pady=0, sticky='ew')
        self.keybind_textbox_clipboard.insert(tk.END, "control+shift")
        self.keybind_textbox_clipboard.configure(state=tk.DISABLED)
        

        self.select_frame_by_name("home")

        self.text_decoder_label = customtkinter.CTkLabel(self.settings_frame, text="API Credentials Path",
                                                         font=customtkinter.CTkFont(size=15, weight="bold"))
        self.text_decoder_label.grid(row=10, column=0, padx=0, pady=0, sticky="n")

        self.filepath_textbox = customtkinter.CTkTextbox(self.settings_frame, width=435, height=25)
        self.filepath_textbox.grid(row=13, column=0, padx=20, pady=0, sticky='ew')
        self.filepath_textbox.configure(state=tk.DISABLED)

        self.filepath_button = customtkinter.CTkButton(self.settings_frame, text="Select File",
                                                       text_color=("gray10", "gray90"), width=100, height=25,
                                                       command=self.open_file_dialog)
        self.filepath_button.grid(row=12, column=0, padx=20, pady=0, sticky="ew")


        #setup for the custom screenshot keybind insertion
        self.keybind_label = customtkinter.CTkLabel(self.settings_frame, text="Custom Screenshot Keybind",
                                                         font=customtkinter.CTkFont(size=15, weight="bold"))
        self.keybind_label.grid(row=14, column=0, padx=0, pady=2, sticky="n")

        self.keybind_textbox = customtkinter.CTkTextbox(self.settings_frame, width=435, height=25)
        self.keybind_textbox.grid(row=16, column=0, padx=20, pady=0, sticky='ew')
        self.keybind_textbox.insert(tk.END, "alt+shift")
        self.keybind_textbox.configure(state=tk.DISABLED)

        self.keybind_button = customtkinter.CTkButton(self.settings_frame, text="Record Input - Press Escape to End",
                                                       text_color=("gray10", "gray90"), width=100, height=25,
                                                       command=self.record_keybind_button_hanlder)
        self.keybind_button.grid(row=15, column=0, padx=20, pady=0, sticky="ew")
    

        


        # Queue Setup
        self.cmd_queue = queue.Queue()
        self.process_commands()

        # Threading Setup
        self.icon_thread = None
        self.icon = None

        # Settings Setup
        self.SETTINGS_FILE = 'grabby_settings.json'
        self.settings = {}  
        self.load_settings()  

    def load_settings(self):
        """
        Load settings from the settings file
        """
        if os.path.isfile(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as f:
                settings = json.load(f)

                #hotkey setup
                self.clipboard_hotkey = keyboard.add_hotkey(settings['clipboardKeybind'],self.queue_copy_clipboard)
                self.screenshot_hotkey = keyboard.add_hotkey(settings['screenshotKeybind'], self.queue_take_screenshot)

                self.keybind_textbox.configure(state=tk.NORMAL)
                self.keybind_textbox_clipboard.configure(state=tk.NORMAL)
                self.keybind_textbox_handler(settings['screenshotKeybind'])
                self.keybind_textbox_handler_clipboard(settings['clipboardKeybind'])
                self.keybind_textbox.configure(state=tk.DISABLED)
                self.keybind_textbox_clipboard.configure(state=tk.DISABLED)


                #credentials setup
                self.credentials = settings['Credentials']

                self.filepath_textbox.configure(state=tk.NORMAL)
                self.filepath_textbox.insert('1.0', self.credentials)  # Insert the filepath into the textbox
                self.filepath_textbox.configure(state=tk.DISABLED)


                #appearance mode setup
                self.appearance_mode_menu.set(settings['appearanceMode'])

                #decoder setup
                self.useGoogleVision = settings['decoder'] == 'Google Vision'
                self.settings_button1.set(settings['decoder'])

                self.settings = settings

        else:

            # If the settings file doesn't exist, initialize with defaults
            self.settings  = {'clipboardKeybind': 'control+shift', 'screenshotKeybind': 'alt+shift','decoder': 'PyTesseract', 'Credentials': '', 'appearanceMode': 'System'}

            self.clipboard_hotkey = keyboard.add_hotkey(self.settings['clipboardKeybind'],self.queue_copy_clipboard)
            self.screenshot_hotkey = keyboard.add_hotkey(self.settings['screenshotKeybind'], self.queue_take_screenshot)

            self.save_settings()  # Create the settings file
        
        
    
    def save_settings(self):
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

        



    def queue_copy_clipboard(self):
        self.cmd_queue.put("Copy Clipboard")
    
    def queue_take_screenshot(self):
        """
        This function adds a "Take Screenshot" command to the queue.
        """
        self.cmd_queue.put("Take Screenshot")

    def stop_icon_thread(self):
        """
        This function adds a "Stop Icon Thread" command to the queue.
        """
        self.cmd_queue.put("Stop Icon Thread")

    def maximize(self):
        """
        This function adds a "Maximize" command to the queue.
        """
        self.cmd_queue.put("Maximize")

    def minimize(self):
        """
        This function adds a "Minimize" command to the queue.
        """
        self.cmd_queue.put("Minimize")

    def process_commands(self):
        """
        This function processes commands from the queue in a non-blocking way. It handles
        four types of commands: "Take Screenshot", "Stop Icon Thread", "Maximize", and "Minimize".
        """
        try:
            cmd = self.cmd_queue.get_nowait()

            if cmd == 'Take Screenshot':
                self.capture_text_button()
                
            elif cmd == "Copy Clipboard":
                self.capture_from_clipboard()

            elif cmd == "Stop Icon Thread":
                self.icon_thread.join()

            elif cmd == "Minimize":
                self.withdraw()
                self.isMinimized = True

            elif cmd == "Maximize":
                self.deiconify()
                self.update()
                self.isMinimized = False

        except queue.Empty:
            pass

        # Check the queue again after 100ms
        self.after(100, self.process_commands)
        
    def capture_from_clipboard(self):
        img = ImageGrab.grabclipboard()
        if img:
            if self.useGoogleVision == True:
                self.screenshot_handler.google_vision_extract_text(img)
            else:
                self.screenshot_handler.pytesseract_extract_text(img)

    def create_sys_tray_icon(self):
        """
        Create system tray icon with "Show" and "Quit" actions. Minimize the app using the Queue
        """
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images", "logo_icon.ico")
        image = Image.open(image_path)
        menu = (item('Show', self.show_from_tray), item('Quit', self.stop_program))
        self.icon = pystray.Icon("name", image, "Grabby", menu)
        self.minimize_app()

    def show_from_tray(self):
        """
        Show the app from the system tray while making sure the tray icon thread is ended using the Queue
        """
        self.icon.stop()
        if self.icon_thread.is_alive():
            self.stop_icon_thread()

        self.maximize()

    def stop_program(self):
        """
        Stop the application and the tray icon thread
        """
        self.icon.stop()
        self.quit()

    def minimize_app(self):
        """
        Minimize the application to the system tray and spin up the tray icon thread
        """
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()
        self.minimize()

    def open_file_dialog(self):
        """
        Open a file dialog to select JSON files for usage with the Google API
        """
        self.filepath_textbox.configure(state=tk.NORMAL)
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

        if file_path:
            self.credentials = file_path
            self.settings['apiCredentials'] = file_path
            self.save_settings()
            self.filepath_textbox.insert('1.0', file_path)  # Insert the filepath into the textbox
        self.filepath_textbox.configure(state=tk.DISABLED)

    def api_button_handler(self, value):
        """
        Handle the API selection button event. If no API file is chosen then prompt for one
        """
        if value == "PyTesseract":
            self.useGoogleVision = False
            self.settings["decoder"] = "PyTesseract"
            self.save_settings()
        else:
            if self.credentials is None:
                self.open_file_dialog()
            if self.credentials is None:
                self.useGoogleVision = False
                self.settings_button1.set("PyTesseract")
                return
            self.useGoogleVision = True
            self.settings["decoder"] = "Google Vision"
            self.save_settings()


    def capture_text_button(self):
        """
        Capture text from the screen on button event or being called from Queue processing
        """
        images = self.screenshot_handler.grab_screenshots()
        for idx, screen in enumerate(get_monitors()):
            window = self.screenshot_handler.create_image_window(screen, images[idx], idx)
            self.windows.append(window)

    def read_from_file(self):
        """
        Read from an image file. Then, based on the selected OCR technology, pass the needed information for extraction
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            img = Image.open(file_path)
            if self.useGoogleVision:
                self.screenshot_handler.google_vision_extract_text(file_path)
            else:
                self.screenshot_handler.pytesseract_extract_text(img)

    def select_frame_by_name(self, name):
        """
        Select a frame by name. Set button color for selected button, then select the correct frame based on button
        clicked
        """
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.history_button.configure(fg_color=("gray75", "gray25") if name == "history_frame" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings_frame" else "transparent")

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
        """
        Handle the home button event by changing the current frame to home.
        """
        self.select_frame_by_name("home")

    def history_button_event(self):
        """
        Handle the history button event by changing the current frame to history.
        """
        self.select_frame_by_name("history_frame")

    def settings_button_event(self):
        """
        Handle the settings button event by changing the current frame to settings.
        """
        self.select_frame_by_name("settings_frame")

    def change_appearance_mode_event(self, new_appearance_mode):
        """
        Change the appearance mode of the application to handle Light and Dark mode.
        """
        customtkinter.set_appearance_mode(new_appearance_mode)

    def clearhistory(self):
        """
        Clear the history. First will set the Tkinter textbox state to normal so text can be changed and
        then all the text will be deleted.
        """
        self.history = []
        self.history_textbox.configure(state=tk.NORMAL)
        self.history_textbox.delete("1.0", tk.END)
        self.history_textbox.configure(state=tk.DISABLED)

    def historylength(self, num):
        """
        Set the history size to a number between 0 and 10, inclusive.
        If the input is not a number or outside the range, ignore it.
        """
        try:
            if 0 <= num <= 10:
                self.historysize = num
            else:
                pass
        except ValueError:
            pass
    
    def record_keybind_button_hanlder(self):
        """
        Record the keybind for taking a screenshot
        """
        keybind = keyboard.record(until='esc')
        if not keybind:
            self.keybind_textbox_handler("alt+shift")
            
        
        keylist = []
        for key in keybind:
            keylist.append(key.name)
        
        keylist.pop()  # Remove the last item in the list which is the esc key
        keybind = keyboard.get_hotkey_name(keylist)
        
        keyboard.remove_hotkey(self.screenshot_hotkey)
        self.screenshot_hotkey = keyboard.add_hotkey(keybind, self.queue_take_screenshot)
        self.settings['screenshotKeybind'] = keybind
        self.save_settings()
        self.keybind_textbox_handler(keybind)
    
    def record_keybind_button_hanlder_clipboard(self):
        """
        Record the keybind for taking a screenshot
        """
        keybind = keyboard.record(until='esc')
        if not keybind:
            self.keybind_textbox_handler("control+shift")
            
        
        keylist = []
        for key in keybind:
            keylist.append(key.name)
        
        keylist.pop()  # Remove the last item in the list which is the esc key
        keybind = keyboard.get_hotkey_name(keylist)
        
        keyboard.remove_hotkey(self.clipboard_hotkey)
        self.clipboard_hotkey = keyboard.add_hotkey(keybind, self.queue_copy_clipboard)
        self.settings['clipboardKeybind'] = keybind
        print(self.settings['clipboardKeybind'])
        print(keybind)
        self.save_settings()
        self.keybind_textbox_handler_clipboard(keybind)

    def keybind_textbox_handler_clipboard(self, text):
        """
        Handle the keybind textbox event by setting the updating the textbox
        """
        self.keybind_textbox_clipboard.configure(state=tk.NORMAL)
        self.keybind_textbox_clipboard.delete("1.0", tk.END)
        self.keybind_textbox_clipboard.insert('1.0', text)
        self.keybind_textbox_clipboard.configure(state=tk.DISABLED)

    def keybind_textbox_handler(self, text):
        """
        Handle the keybind textbox event by setting the updating the textbox
        """
        self.keybind_textbox.configure(state=tk.NORMAL)
        self.keybind_textbox.delete("1.0", tk.END)
        self.keybind_textbox.insert('1.0', text)
        self.keybind_textbox.configure(state=tk.DISABLED)

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # When not bundled with PyInstaller, use the script's directory
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
