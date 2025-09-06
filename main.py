import os
from google import genai
from PIL import Image
from io import BytesIO

API_KEY=os.environ.get("GEMINI_API_KEY")
# -----------------

# Configure the client with your API key
client = genai.Client(api_key=API_KEY)

# Height adjustment variable for positioning
# height_adjustment = "same height"
height_adjustment = "fan slightly taller"
# expression = "while the fan looks happy and excited"
expression = ""

# The text prompt for AI selfie generation with celebrity
prompt = f"Create a realistic selfie photo showing the fan taking a picture with the celebrity. The fan should be positioned next to the celebrity in a natural, casual pose as if they met and are taking a selfie together. Both people should be at {height_adjustment} level. Make it look authentic with proper lighting, shadows, and perspective. Both the celebrity and fan should maintain their professional appearance{expression}. Ensure both faces are clearly visible and well-lit."

print("Generating image...")

# Load the source images
img = 'kamal.jpeg'
img = 'kamal.png'
with open(img, 'rb') as f:
    celebrity_image_data = f.read()

with open('fan.jpeg', 'rb') as f:
    fan_image_data = f.read()

# Call the API to generate the celebrity selfie
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[
        prompt,
        genai.types.Part(
            inline_data={
                "mime_type": "image/jpeg",
                "data": celebrity_image_data
            }
        ),
        genai.types.Part(
            inline_data={
                "mime_type": "image/jpeg", 
                "data": fan_image_data
            }
        )
    ],
    config={
        "seed": 42,
        "temperature": 0
    }
)

image_parts = [
    part.inline_data.data
    for part in response.candidates[0].content.parts
    if part.inline_data
]
 
if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    output_filename = 'celebrity_selfie.png'
    image.save(output_filename)
    print(f"Celebrity selfie saved as '{output_filename}'")
    
    # Check if input and output are the same
    fan_image = Image.open('fan.jpeg')
    output_image = Image.open(output_filename)
    
    # Compare images by converting to RGB and comparing pixel data
    if fan_image.size == output_image.size:
        fan_rgb = fan_image.convert('RGB')
        output_rgb = output_image.convert('RGB')
        
        # Compare pixel by pixel
        pixels_different = 0
        total_pixels = fan_rgb.size[0] * fan_rgb.size[1]
        
        for x in range(fan_rgb.size[0]):
            for y in range(fan_rgb.size[1]):
                if fan_rgb.getpixel((x, y)) != output_rgb.getpixel((x, y)):
                    pixels_different += 1
        
        similarity_ratio = (total_pixels - pixels_different) / total_pixels
        
        if similarity_ratio > 0.95:  # 95% similar
            print(f"WARNING: Fan photo and generated selfie are {similarity_ratio:.2%} similar. Stopping process.")
            exit(0)
        else:
            print(f"Images are {similarity_ratio:.2%} similar - proceeding with verification.")
    
    # Verification prompt for celebrity selfie
    verify_prompt = "Analyze this generated celebrity selfie and verify: 1) Both the fan and celebrity are clearly visible and recognizable, 2) The selfie looks natural and realistic with proper perspective, 3) Lighting and shadows are consistent and believable, 4) The fan appears happy and excited while the celebrity maintains their professional appearance. Rate each aspect 1-10 and provide overall authenticity score."
    
    print("Verifying generated image...")
    verify_response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[
            verify_prompt,
            genai.types.Part(
                inline_data={
                    "mime_type": "image/png",
                    "data": image_parts[0]
                }
            )
        ],
    )
    
    print("Verification result:")
    print(verify_response.candidates[0].content.parts[0].text)