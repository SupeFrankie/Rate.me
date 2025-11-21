from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def crop_center_square(image):
    """Crop image to center square with no lost quality"""
    width, height = image.size
    
    size = min(width,height)
    
    #Crop box dimensions
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top +size
    
    # Crop to square
    return image.crop((left, top, right, bottom))


def process_profile_picture(uploaded_file, max_size=800):
    """
    Process uploaded profile picture:
    - Crop to square
    - Resize if too large
    - Maintain quality
    - Convert to RGB if needed
    """
    try:
        # Open the image
        img = Image.open(uploaded_file)
        
        # Convert RGBA to RGB (for PNGs with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Crop to center square
        img = crop_center_square(img)
        
        # Resize if too large (maintain aspect ratio since it's square)
        if img.size[0] > max_size:
            img = img.resize((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to BytesIO with high quality
        output = BytesIO()
        img.save(output, format='JPEG', quality=95, optimize=True)
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{uploaded_file.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return uploaded_file  # Return original if processing fails