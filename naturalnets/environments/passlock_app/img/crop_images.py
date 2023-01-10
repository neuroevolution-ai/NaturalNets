from PIL import Image
import os

folder_path = 'naturalnets\environments\passlock_app\img\manual_page_img'

# Iterate through all files in the folder
for file in os.listdir(folder_path):
  # Check if the file is a png file
  if file.endswith(".png"):
    # Open the image
    image = Image.open(os.path.join(folder_path, file))

    # Get the dimensions of the image
    width, height = image.size

    # Set the new dimensions of the image
    new_width = width
    new_height = height

    # Crop the image to the new dimensions
    cropped_image = image.crop((0, 30, new_width, new_height))

    # Save the cropped image
    cropped_image.save(os.path.join(folder_path, file))
