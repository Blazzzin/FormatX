#Author: Saheer Multani
#JPEG (.jpg, .jpeg)
#PNG (.png)
#BMP (.bmp)
#GIF (.gif)
#TIFF (.tiff, .tif)
#ICO (.ico)
#WEBP (.webp)
#PPM (.ppm)
#PGM (.pgm)
#EPS (.eps)
from PIL import Image

def convert_image(input_path, output_path):
    image = Image.open(input_path)
    if image.mode == 'RGBA' and output_path.lower().endswith('.jpg'):
        # Convert RGBA to RGB
        image = image.convert('RGB')
    image.save(output_path)

def selected_options(option):
    if option == "JPEG":
        return ".jpg"
    elif option == "PNG":
        return ".png"
    elif option == "BMP":
        return ".bmp"
    else:
        return None