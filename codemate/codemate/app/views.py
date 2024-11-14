from django.shortcuts import render
import requests
import json
import re
import whisper
from pydub import AudioSegment

def data(request):
    return render(request ,'input.html')

# API URL and key (replace with your actual API key)
url = "https://api.x.ai/v1/chat/completions"
api_key = "xai-4BKmkPMUL6Vbj5SGX5vC4Y4aR4Wp9m5gOTSQFrU2Dx6DpERGkGzZOu0aLy2A1F0Qj63nv67oFWWIFoxa"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

def get_bot_response(messages):
    """Get response from the chatbot API."""
    data = {
        "messages": messages,
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()  # Return the JSON response from the API
    else:
        return {"error": "Failed to call API"}

import re

def home(request):
    """Render the home page with input fields and chatbot."""
    
    # Initialize message history (empty list initially)
    if 'message_history' not in request.session:
        request.session['message_history'] = []

    # Data to be sent to the template (start with an empty dictionary)
    sent_data = {}

    if request.method == 'POST':
        # Retrieve data from form
        user_message = request.POST.get("user_message", "")
        section_type = request.POST.get("section_type", "")

        # Add user message to history
        if user_message:
            request.session['message_history'].append({"role": "user", "content": user_message})

            # Prepare messages for bot API
            messages = [{"role": "system", "content": "You are Grok, which speaks very articulately."}]
            messages.extend(request.session['message_history'])  # Include the history in the API request

            # Get bot response (replace this with your bot API call logic)
            bot_response = get_bot_response(messages)  # Assuming you have a function for this
            bot_message = bot_response.get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I didn\'t understand that.')

            # Add bot's response to history
            request.session['message_history'].append({"role": "assistant", "content": bot_message})

        # Handle audio file upload for speech-to-text conversion
        audio_file = request.FILES.get('audio_file', None)
        if audio_file:
            # Convert WAV to MP3 using pydub
            wav_file_path = f'temp/{audio_file.name}'
            mp3_file_path = f'temp/{audio_file.name.rsplit(".", 1)[0]}.mp3'
            
            with open(wav_file_path, 'wb+') as temp_wav:
                for chunk in audio_file.chunks():
                    temp_wav.write(chunk)

            # Convert WAV to MP3
            audio_segment = AudioSegment.from_wav(wav_file_path)
            audio_segment.export(mp3_file_path, format='mp3')

            # Transcribe audio using Whisper AI model
            transcribed_text = transcribe_audio(mp3_file_path)

            if transcribed_text:
                request.session['message_history'].append({"role": "user", "content": transcribed_text})
                
                # Prepare messages for bot API with transcribed text
                messages.append({"role": "user", "content": transcribed_text})
                
                # Get bot response for transcribed text (replace with your API call logic)
                bot_response = get_bot_response(messages)
                bot_message = bot_response.get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I didn\'t understand that.')
                
                # Add bot's response to history
                request.session['message_history'].append({"role": "assistant", "content": bot_message})

            # Clean up temporary files (optional but recommended)
            os.remove(wav_file_path)  # Remove temporary WAV file
            os.remove(mp3_file_path)  # Remove temporary MP3 file

        # Save the updated message history to the session
        request.session.modified = True

    return render(request, 'index.html', {
        'message_history': request.session['message_history'],
        'sent_data': sent_data  # Pass only the relevant data to the template
    })

def transcribe_audio(audio_file):
    """Transcribe audio using Whisper AI model."""
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_file)  # Transcribe the audio file
    return result['text']

def handle_link(link):
    """Handle the link input."""
    # Logic to process the link data (e.g., save it to the database or perform other operations)
    print(f"Handling link: {link}")

def handle_youtube_link(yt_link):
    """Handle the YouTube link input."""
    # Logic to process the YouTube link data (e.g., extract video info, etc.)
    print(f"Handling YouTube link: {yt_link}")

def handle_text(text):
    """Handle the text input."""
    # Logic to process the text data (e.g., save it, analyze it, etc.)
    print(f"Handling text: {text}")

def handle_pdf(pdf):
    """Handle the PDF file upload."""
    # Logic to handle PDF (e.g., save the PDF, extract text, etc.)
    if pdf:
        print(f"Handling PDF: {pdf.name}")
    else:
        print("No PDF uploaded")

'''
def home(request):
    """Render the home page with input fields and chatbot."""
    
    # Initialize message history (empty list initially)
    if 'message_history' not in request.session:
        request.session['message_history'] = []

    if request.method == 'POST':
        user_message = request.POST.get("user_message", "")
        
        # Add user message to history
        if user_message:
            request.session['message_history'].append({"role": "user", "content": user_message})

            # Prepare messages for bot API
            messages = [{"role": "system", "content": "You are Grok, which speaks very articulately."}]
            messages.extend(request.session['message_history'])  # Include the history in the API request

            # Get bot response
            bot_response = get_bot_response(messages)
            bot_message = bot_response.get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I didn\'t understand that.')

            # Add bot's response to history
            request.session['message_history'].append({"role": "assistant", "content": bot_message})

        # Save the updated message history to the session
        request.session.modified = True

    return render(request, 'index.html', {
        'message_history': request.session['message_history']
    })
'''