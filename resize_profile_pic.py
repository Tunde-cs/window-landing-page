from PIL import Image

# Load the original image
img_path = 'media/profile_pics/ediomi12.jpg'
img = Image.open(img_path)

# Resize to 48x48 (square)
img = img.resize((48, 48), Image.LANCZOS)

# Save it as a new file to avoid overwriting
img.save('media/profile_pics/ediomi12_thumb.jpg')

print("✅ Profile picture resized successfully!")

