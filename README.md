# rgbcym_extractor

A Python script that automatically processes fluorescence/color images to detect, mask, and count spots across 6 specific color channels (Red, Green, Blue, Yellow, Cyan, and Magenta) representing different genes. 

## Features
* **Auto-Calibration:** Uses percentile-based thresholding to dynamically adjust to different image brightness and contrast levels.
* **Color Masking:** Isolates specific colors and generates black-and-white mask images for verification.
* **Blob Detection:** Uses OpenCV's `SimpleBlobDetector` to count distinct spots in each color channel.
* **Batch Processing:** Automatically finds and processes all common image files (`.jpg`, `.png`, `.tif`, etc.) in the folder.
* **Excel Export:** Aggregates all spot counts across all images and outputs them into a single `.xlsx` file.

## Requirements

You will need Python 3.x installed on your machine. You also need to install the required external libraries. 

You can install all dependencies at once using pip:

Install dependencies
pip install opencv-python numpy pandas openpyxl
