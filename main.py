import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import io

# Function to read the OpenAI API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Function to read prompt instructions from a file
def read_prompt_instructions(file_path):
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
        st.error("Texture image 'texture.png' not found. Using white background.")
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
            st.error(f"Font file '{font_path}' not found. Using default font.")
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

    # Save the image to a BytesIO object
    img_bytes = io.BytesIO()
    canvas.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return canvas, img_bytes

# Main function to handle user choices
def main():
    st.title("Beautiful Hand Written Letters")

    # Initialize the image counter in session state
    if 'image_counter' not in st.session_state:
        st.session_state.image_counter = 215  # Initial value for the image counter

    # Display the current image counter
    st.write(f"Total images generated: {st.session_state.image_counter}")

    # Buttons section
    st.markdown("""
    <div style="display: flex; gap: 10px;">
        <a href="https://x.com/soundhumor" target="_blank">
            <button style="background-color: #FF5F5F; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">Give me feedback</button>
        </a>
        <a href="https://buymeacoffee.com/tanulmittal" target="_blank">
            <button style="background-color: #FF5F5F; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">Buy me a coffee</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Instructions section
    st.markdown("""
    ### Instructions
    1. Choose to input text manually or use an OpenAI API key (requires technical knowledge).
    2. Fill in the required fields.
    3. For manual input, use 120 words for best results.
    4. Click "Generate Image" to create your handwritten letter.
    5. Download the image using the download button.
    6. If you like the app, please support to keep the project going.
    7. Share your feedback to help improve the app.
    """)

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        choice = st.radio("Choose an option:", ("Input text manually", "Use OpenAI API key"))

        if choice == 'Input text manually':
            user_text = st.text_area("Enter your text:")
            if st.button("Generate Image"):
                canvas, img_bytes = create_a4_canvas_with_text(user_text)
                st.session_state.image_counter += 1  # Increment the counter
                with col2:
                    st.image(canvas, caption='Generated Image', use_column_width=True)
                    st.download_button(
                        label="Download Image",
                        data=img_bytes,
                        file_name='a4_canvas_with_text.png',
                        mime='image/png'
                    )
        elif choice == 'Use OpenAI API key':
            api_key = st.text_input("Enter your OpenAI API key:", type="password")
            prompt_instructions = read_prompt_instructions('prompt.txt')
            
            recipient = st.text_input("Name of the person you are sending to:")
            context = st.text_input("Provide some context for the letter:")
            user_name = st.text_input("What is your name?:")
            sending_to = st.text_input("Describe your relation with this person:")
            additional_info = st.text_input("Any additional information you want to include?")

            if st.button("Generate Image"):
                prompt = f"""
                {prompt_instructions}

                Recipient: {recipient}
                Context: {context}
                Sender: {user_name}
                Sending to: {sending_to}
                Additional Information: {additional_info}
                """
                generated_text = generate_text(prompt, api_key)
                canvas, img_bytes = create_a4_canvas_with_text(generated_text)
                st.session_state.image_counter += 1  # Increment the counter
                with col2:
                    st.image(canvas, caption='Generated Image', use_column_width=True)
                    st.download_button(
                        label="Download Image",
                        data=img_bytes,
                        file_name='a4_canvas_with_text.png',
                        mime='image/png'
                    )

if __name__ == "__main__":
    main()
