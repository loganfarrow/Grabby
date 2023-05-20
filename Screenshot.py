
import tkinter as tk
import mss
from PIL import Image, ImageTk
import time
import os
import numpy as np
import cv2
import pytesseract
import pyperclip

#for saving the screenshots to the drive for debugging 
from mss.tools import to_png

# Imports the Google Cloud client library
from google.cloud import vision



class Screenshot:
    def __init__(self):
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
        
        
        # Save the cropped screenshot under a folder screengrabs
        folder_name = "screengrabs"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


        cropped_output_file = f"{folder_name}/cropped_monitor_{canvas.monitor_index}.png"
        cropped_img.save(cropped_output_file)
        print(f"Cropped screenshot saved as {cropped_output_file}")

        #pass the cropped image into the text extractor function
        if(self.useGoogleVision):
            self.google_vision_extract_text(cropped_output_file)
        else:
            self.pytesseract_extract_text(cropped_img)



    def pytesseract_extract_text(self,img):
    
        cv_img = cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
        grayscale = cv2.cvtColor(cv_img,cv2.COLOR_BGR2GRAY)
        
        text = pytesseract.image_to_string(grayscale)

        #send the text to be stored in history
        self.history_handler(text)

    def google_vision_extract_text(path):

        #set the credentials for google vision api
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials


        #basic vision api code given by google
        
        client = vision.ImageAnnotatorClient()

        with open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        print('Texts:')

        for text in texts:
            print(f'\n"{text.description}"')

            vertices = ([f'({vertex.x},{vertex.y})'
                        for vertex in text.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

    

    def history_handler(self,text):

        self.history += [text]

        #debugging
        print(self.history)

        self.historyrolling(self.historysize)

        #copy the text to clipboard
        pyperclip.copy(text)


        self.history_textbox.configure(state=tk.NORMAL)
        self.history_textbox.insert("end", text + "\n")
        self.history_textbox.configure(state=tk.DISABLED)

    def get_history(self):
        return self.history

    

    def historyrolling(self,historysize):
        if historysize == 0:
            return 
        if historysize < len(self.history):
            templist = []
            for i,item in enumerate(self.history):
                templist += [self.history[-(i+1)]]
            templist.reverse()
            self.history = templist


    def create_image_window(self, screen, img, monitor_index):
        window = tk.Toplevel()
        window.overrideredirect(1)
        window.geometry(f"{screen.width}x{screen.height}+{screen.x}+{screen.y}")

        img = img.resize((screen.width, screen.height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        canvas = tk.Canvas(window, width=screen.width, height=screen.height)
        canvas.monitor_index = monitor_index  # Store the monitor index in the canvas
        canvas.monitor = {"left": screen.x, "top": screen.y, "width": screen.width, "height": screen.height}


        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.pack(fill=tk.BOTH, expand=True)

        canvas.bind("<Button-1>", lambda event: self.on_mouse_press(event))
        canvas.bind("<B1-Motion>", lambda event: self.on_mouse_move(event))
        canvas.bind("<ButtonRelease-1>", lambda event: self.on_mouse_release(event))

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
        rect_coordinates = self.draw_rectangle(event.widget, self.x1, self.y1, x2, y2)
        self.capture_smaller_screenshot(event.widget, rect_coordinates)
        for window in self.windows:
            window.destroy()
        
        # Show the main window again and update the UI
        self.update()
        self.deiconify()

    def draw_rectangle(self, canvas, x1, y1, x2, y2):
        canvas.delete("rect")
        rect = canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="rect")
        return (x1, y1, x2, y2)

    def grab_screenshots(self):
        images = []
        self.withdraw()
        self.update()
        time.sleep(.1)
        with mss.mss() as sct:
            # Get the list of monitor dictionaries
            monitors = sct.monitors[1:]  # Exclude the "All in One" monitor

            for idx, monitor in enumerate(monitors, start=1):
                # Capture the screenshot
                screenshot = sct.grab(monitor)

                # Save the screenshot
                folder_name = "screengrabs"
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

                # Save the screenshot under the 'screengrabs' folder
                output_file = f"{folder_name}/monitor_{idx}.png"
                to_png(screenshot.rgb, screenshot.size, output=output_file)
                print(f"Screenshot saved as {output_file}")

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