import tkinter as tk
import mss
from PIL import Image, ImageTk
import time
import os
import numpy as np
import cv2
import pytesseract
import pyperclip
import io


# for saving the screenshots to the drive for debugging
from mss.tools import to_png

# Imports the Google Cloud client library
from google.cloud import vision


class Screenshot:
    def __init__(self, app):
        self.app = app
        self.history = []
        self.historysize = 5

    def capture_smaller_screenshot(self, canvas, rect_coordinates):
        x1, y1, x2, y2 = rect_coordinates
        width = x2 - x1
        height = y2 - y1

        if width <= 0 or height <= 0:
            return

        # Capture the full screenshot
        with mss.mss() as sct:
            monitor = canvas.monitor
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # Crop the screenshot to the selected area
        cropped_img = img.crop((x1, y1, x1 + width, y1 + height))

        # Convert the cropped image to bytes
        byte_arr = io.BytesIO()
        cropped_img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        # pass the cropped image into the text extractor function
        if (self.app.useGoogleVision):
            self.google_vision_extract_text(byte_arr)
        else:
            self.pytesseract_extract_text(cropped_img)

    def pytesseract_extract_text(self, img):

        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        grayscale = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(grayscale)

        # send the text to be stored in history
        self.history_handler(text)

    def google_vision_extract_text(self, image_data):

        # set the credentials for google vision api
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.app.credentials

        # basic vision api code given by google
        client = vision.ImageAnnotatorClient()

        # Use the image data directly
        image = vision.Image(content=image_data)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        full_text = ""
        if texts:
            full_text = texts[0].description

        self.history_handler(full_text)

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

    def history_handler(self, text):

        self.history += [text]

        self.historyrolling(self.historysize)

        # copy the text to clipboard
        pyperclip.copy(text)

        self.app.history_textbox.configure(state=tk.NORMAL)
        self.app.history_textbox.insert("end", text + "\n")
        self.app.history_textbox.configure(state=tk.DISABLED)

    def get_history(self):
        return self.history

    def historyrolling(self, historysize):
        if historysize == 0:
            return
        if historysize < len(self.history):
            templist = []
            for i, item in enumerate(self.history):
                templist += [self.history[-(i + 1)]]
            templist.reverse()
            self.history = templist

    def create_image_window(self, screen, img, monitor_index):
        window = tk.Toplevel()
        window.overrideredirect(1)
        window.geometry(
            f"{screen.width}x{screen.height}+{screen.x}+{screen.y}")

        img = img.resize((screen.width, screen.height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        canvas = tk.Canvas(window, width=screen.width, height=screen.height)
        canvas.monitor_index = monitor_index  # Store the monitor index in the canvas
        canvas.monitor = {
            "left": screen.x,
            "top": screen.y,
            "width": screen.width,
            "height": screen.height}

        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.pack(fill=tk.BOTH, expand=True)

        canvas.bind("<Button-1>", lambda event: self.on_mouse_press(event))
        canvas.bind("<B1-Motion>", lambda event: self.on_mouse_move(event))
        canvas.bind(
            "<ButtonRelease-1>",
            lambda event: self.on_mouse_release(event))

        # Store the photo reference in the window to prevent garbage collection
        window.photo = photo

        return window

    def on_mouse_press(self, event):
        self.x1, self.y1 = event.x, event.y

    def on_mouse_move(self, event):
        x2, y2 = event.x, event.y
        self.draw_rectangle(event.widget, self.x1, self.y1, x2, y2)

    def on_mouse_release(self, event):
        x2, y2 = event.x, event.y
        rect_coordinates = self.draw_rectangle(
            event.widget, self.x1, self.y1, x2, y2)
        self.capture_smaller_screenshot(event.widget, rect_coordinates)
        for window in self.app.windows:
            window.destroy()

        # Show the main window again and update the UI
        if not self.app.isMinimized:
            self.app.update()
            self.app.deiconify()

    def draw_rectangle(self, canvas, x1, y1, x2, y2):
        canvas.delete("rect")
        rect = canvas.create_rectangle(
            x1, y1, x2, y2, outline="red", tags="rect")
        return (x1, y1, x2, y2)

    def grab_screenshots(self):
        images = []

        if not self.app.isMinimized:
            self.app.withdraw()
            self.app.update()

        time.sleep(.1)
        with mss.mss() as sct:
            # Get the list of monitor dictionaries
            monitors = sct.monitors[1:]  # Exclude the "All in One" monitor

            for idx, monitor in enumerate(monitors, start=1):
                # Capture the screenshot
                screenshot = sct.grab(monitor)

                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                images.append(img)

            return images

    def show_screenshot(self, screenshot):
        # Create a new window to display the captured screenshot
        screenshot_window = tk.Toplevel(self)
        screenshot_window.title("Captured Screenshot")

        # Convert the screenshot to a PhotoImage and display it in a label
        img = ImageTk.PhotoImage(screenshot)
        label = tk.Label(screenshot_window, image=img)
        label.image = img
        label.pack()
