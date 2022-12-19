from PIL import Image

# Open the image
image = Image.open('naturalnets\environments\passlock_app\img\main_window_page.png')

# Get the dimensions of the image
width, height = image.size
print(width)
print(height)
# Set the new dimensions of the image
new_width = width
new_height = height

# Crop the image to the new dimensions
cropped_image = image.crop((0, 32, new_width, new_height))

# Save the cropped image
cropped_image.save('naturalnets\environments\passlock_app\img\main_window_page.png')
