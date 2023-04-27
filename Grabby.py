import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageGrab, ImageTk, ImageOps, ImageFilter
import pyscreenshot as ImageGrab
import numpy as np
import time
import sv_ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Sniper")
        self.geometry("300x200")


        # Apply the sv-ttk theme
        sv_ttk.set_theme("dark")
        

        # Create a 'Grab' button and add it to the main window
        self.grab_button = ttk.Button(self, text="Grab", command=self.grab_screen)
        self.grab_button.place(relx=0.5, rely=0.5, anchor='center')



    def grab_screen(self):
        # Hide the main window and update the UI
        self.withdraw()
        self.update()
        time.sleep(.01)

        # Take a screenshot and apply a blur filter to create a darkened background
        self.full_screen_img = ImageGrab.grab()  # Store the original screen image
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.full_screen_img = self.full_screen_img.resize((screen_width, screen_height))

        blurred_screen_img = self.full_screen_img.filter(ImageFilter.GaussianBlur(0.1))

        self.create_overlay(self.full_screen_img)





    def create_overlay(self, screen_img):
        overlay = tk.Toplevel(self)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 1)
        overlay.configure(bg="black")

        canvas = tk.Canvas(overlay, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self.tk_img = ImageTk.PhotoImage(screen_img)
        canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        canvas.bind("<Button-1>", self.on_button_press)
        canvas.bind("<B1-Motion>", self.on_move_press)
        canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.start_x = None
        self.start_y = None
        self.rect_id = None

        overlay.mainloop()


    def on_button_press(self, event):
        # Save the initial mouse press coordinates and draw a rectangle on the canvas
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = event.widget.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red")

    def on_move_press(self, event):
        # Update the rectangle coordinates while the user is dragging the mouse
        curX = event.x
        curY = event.y
        event.widget.coords(self.rect_id, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        

        # Determine the screenshot coordinates based on the drawn rectangle
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        # Capture the screenshot using the coordinates
        screenshot = self.full_screen_img.crop((x1, y1, x2, y2))
        # Add your OpenCV logic here

        # Close the overlay window
        event.widget.master.destroy()
        
        # Show the main window again and update the UI
        self.update()
        self.deiconify()


        # Display the captured screenshot in a new window
        self.show_screenshot(screenshot)

    def show_screenshot(self, screenshot):
        # Create a new window to display the captured screenshot
        screenshot_window = tk.Toplevel(self)
        screenshot_window.title("Captured Screenshot")

        # Convert the screenshot to a PhotoImage and display it in a label
        img = ImageTk.PhotoImage(screenshot)
        label = tk.Label(screenshot_window, image=img)
        label.image = img
        label.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()

