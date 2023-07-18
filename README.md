# Grabby
Grabby is a modern screenshot utility made to capture screenshots and automatically extract text from them using either Python Tesseract or the Google Vision API. In addition, it includes a unique history storage feature and maintains functionality when minimized.

# Features
* Text Extraction: Grabby can take screenshots with a built-in capture function and push the text to your clipboard.
* Copy from Clipboard: Grabby can replace images on your clipboard with the text that is inside of them.
* File Transcription: Import image files directly and transcribe the text inside.
* History Storage: Grabby features a unique history storage tab, where you can easily access all your extracted text from your current session.
* Minimalistic Design: Grabby can be minimized while retaining full functionality, keeping your workspace clean and uncluttered.

# Getting Started
Follow the steps below to get started with Grabby.

# Requirements
* Python 3.6 or higher
* A Windows device

### Step 1: Install Dependencies
Before running the program, you need to install the necessary Python libraries.

```bash
pip install pytesseract
pip install google-cloud-vision
pip install customtkinter
pip install mss
pip install Pillow
pip install numpy
pip install opencv-python
pip install pyperclip
pip install keyboard
pip install pystray
pip install screeninfo
```
Note: Depending on your Python installation, you may need to use pip3 instead of pip.

### Step 2: Clone the Repository
Clone the repository using the following command:

```bash
git clone https://github.com/loganfarrow/grabby.git
```

### Step 3: Run Grabby
Navigate to the directory containing Grabby and run the following command:

```bash
python grabby.py
```

Note: Depending on your Python installation, you may need to use python3 instead of python.

### (OPTIONAL) Step 4: Setup Google Vision API
Google Vision generally provides superior text recognition than Pytesseract. However, it requires an internet connection and only 1,000 free uses per month are provided, but that is enough for most users. 

Follow the instructions provided in [this link](https://cloud.google.com/vision/docs/setup)  to get your Google Vision API JSON file.

Then download the file, go to Grabby -> Settings -> API Credentials Path and select the file. Be sure to change the Text Decoder option to Google Vision.

### Enjoy! If you run into any issues or have any suggestions, please file an issue on the GitHub page for this project. Contributions to this project are welcome and appreciated!

