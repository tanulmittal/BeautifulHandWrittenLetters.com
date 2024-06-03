from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

# Function to read the OpenAI API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Function to generate text using OpenAI GPT-3.5 Turbo
def generate_text(prompt, api_key):
    client = OpenAI(api_key=api_key)  # Initialize the client with the correct API key
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to wrap text
def wrap_text(text, font, max_width):
    paragraphs = text.split('\n')
    wrapped_text = []
    for paragraph in paragraphs:
        lines = []
        words = paragraph.split()
        while words:
            line = ''
            while words:
                proposed_line = line + (words[0] + ' ')
                bbox = font.getbbox(proposed_line)
                if bbox[2] <= max_width:
                    line = proposed_line
                    words.pop(0)
                else:
                    break
            lines.append(line)
        wrapped_text.append('\n'.join(lines))
    return '\n'.join(wrapped_text)

# Function to create an A4 canvas with text
def create_a4_canvas_with_text(user_text):
    # Define A4 size in pixels (300 DPI)
    a4_width, a4_height = 2480, 3508

    # Open the texture image
    try:
        canvas = Image.open('texture.png')
        canvas = canvas.resize((a4_width, a4_height))  # Resize to A4 size
    except IOError:
        print("Texture image 'texture.png' not found. Using white background.")
        canvas = Image.new('RGB', (a4_width, a4_height), 'white')

    # Initialize ImageDraw
    draw = ImageDraw.Draw(canvas)

    # Define text properties
    text_color = 'blue'
    font_size = 70  # Initial font size
    font_path = "HomemadeApple-Regular.ttf"  # Path to the font file

    while True:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font file '{font_path}' not found. Using default font.")
            font = ImageFont.load_default()

        # Wrap the text
        wrapped_text = wrap_text(user_text, font, a4_width - 200)

        # Calculate the size of the wrapped text
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_height = bbox[3] - bbox[1]

        if text_height <= a4_height - 200:
            break
        else:
            font_size -= 10  # Reduce font size if text doesn't fit

    # Define text position
    text_x, text_y = 150, 150  # Starting position of the text

    # Draw the wrapped text on the canvas
    draw.multiline_text((text_x, text_y), wrapped_text, fill=text_color, font=font, spacing=40)

    # Save the image
    canvas.save('a4_canvas_with_text.png')

    # Print confirmation message
    print("Image generated")

# Read the OpenAI API key
api_key = read_api_key('key.txt')

# Read the prompt instructions from the file
with open('prompt.txt', 'r') as file:
    prompt_instructions = file.read()

# Prompt the user for inputs
recipient = input("Name of the person you are sending to: ")
context = input("Provide some context for the letter: ")
user_name = input("What is your name?: ")
sending_to = input("Describe your relation with this person: ")
additional_info = input("Any additional information you want to include? ")

# Create the prompt for the OpenAI model following the instructions
prompt = f"""
{prompt_instructions}

Recipient: {recipient}
Context: {context}
Sender: {user_name}
Sending to: {sending_to}
Additional Information: {additional_info}
"""

# Generate text using OpenAI GPT-3.5 Turbo
generated_text = generate_text(prompt, api_key)

# Save the generated text to input.txt
with open('input.txt', 'w') as file:
    file.write(generated_text)

# Create the canvas with the generated text
create_a4_canvas_with_text(generated_text)
