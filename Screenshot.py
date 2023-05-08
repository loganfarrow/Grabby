
import tkinter as tk
import mss
from PIL import Image, ImageTk
import time
import os

#for saving the screenshots to the drive for debugging 
from mss.tools import to_png



class Screenshot:
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
        #self.show_screenshot(screenshot)
        
        # Save the cropped screenshot under a folder screengrabs
        folder_name = "screengrabs"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


        cropped_output_file = f"{folder_name}/cropped_monitor_{canvas.monitor_index}.png"
        cropped_img.save(cropped_output_file)
        print(f"Cropped screenshot saved as {cropped_output_file}")

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