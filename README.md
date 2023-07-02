# Grabby
Grabby is a modern and efficient screenshot utility to capture screenshots and automatically extract text from them using your choice of Tesseract or the Google Vision API. In addition, it includes a unique history storage feature and maintains functionality even when minimized.

# Features
* Screenshots: Capture screenshots with either the built in capture code, or use the windows snipping tool hotkey
* Text Extraction: Utilize either PyTesseract or the Google Vision API to extract text from the screenshots and have them saved to your clipboard
* File Transcription: Upload image files directly and transcribe the text within.
* History Storage: Grabby features a unique history storage tab, where you can easily access all your past screenshots and their associated extracted text.
* Minimalistic Design: Grabby can be minimized while retaining full functionality, keeping your workspace clean and uncluttered.

# Getting Started
Follow the steps below to get started with Grabby.

### Prerequisites
* Python (>=3.6)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* Google Vision API or Tesseract OCR
* All Other Dependencies Found in Grabby and Screenshot

### Step 1: Install Dependencies
Before running the app, you need to install the necessary Python libraries. See above!

```bash
pip install pytesseract
pip install google-cloud-vision
pip install customtkinter
```
Note: Depending on your Python installation, you may need to use pip3 instead of pip.

### Step 2: Setup Google Vision API / Tesseract
* Google Vision API: Follow the instructions provided in [this link](https://cloud.google.com/vision/docs/setup)  to get your Google Vision API JSON file.

* Tesseract: Download and install Tesseract using the instructions provided in [this link](https://github.com/tesseract-ocr/tesseract).

Install Both! Ensure you have set the appropriate environment variables for either Google Vision API or Tesseract.

### Step 3: Clone the Repository
Clone the repository using the following command:

```bash
git clone https://github.com/loganfarrow/grabby.git
```

### Step 4: Run Grabby
Navigate to the directory containing Grabby and run the following command:

```bash
python grabby.py
```

Note: Depending on your Python installation, you may need to use python3 instead of python.

### Enjoy! If you run into any issues or have any suggestions, please file an issue on the GitHub page for this project. Contributions to this project are welcome and appreciated!
