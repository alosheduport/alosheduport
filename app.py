import os
import streamlit as st
import google.generativeai as genai
from io import StringIO

# Set your API key
API_KEY = 'AIzaSyC0lHNZsII28Ayvgivo9rVJVkrFDAbW6MM'
genai.configure(api_key=API_KEY)

# Define your generative models
model = genai.GenerativeModel("gemini-exp-1206")
itsus = genai.GenerativeModel("gemini-1.5-flash-8b")

# Checklist to be checked
checklist = [
    "Intro", 
    "Continuation of previous call (catching up on stuff)", 
    "Academics (importance of live, exam, pyq, status at school academics)", 
    "Parents connection: Dashboard activity",
    "Staying in-topic (not deviating from the main topic)",
    "Conclusion", 
    "Rapport building"
]

# Streamlit UI components
st.title('Audio Transcript and Call Evaluation')
st.subheader("Upload your audio file (MP3 format) for transcription and evaluation:")

# File upload widget
audio_file = st.file_uploader("Choose an audio file", type=["mp3"])

if audio_file:
    st.write(f"Processing file: {audio_file.name}")
    
    # Save the uploaded audio file temporarily
    temp_audio_path = os.path.join("temp", audio_file.name)
    with open(temp_audio_path, "wb") as f:
        f.write(audio_file.getbuffer())
    
    # Upload the file to the generative AI model
    myfile = genai.upload_file(temp_audio_path)
    
    # Generate content (transcription in English)
    result = model.generate_content([myfile, "Give the transcription in English"])
    transcription = result.text
    
    # Display the transcription in the app
    st.subheader("Transcript:")
    st.text_area("Transcription", transcription, height=300)
    
    # Evaluate the checklist using the itsus model
    ratings = []
    for item in checklist:
        prompt = f"Rate the following on a scale of 1-5 based on the provided transcript: '{item} and return the rating as a number only'"
        response = itsus.generate_content(f"{prompt}\n\nTranscript: {transcription}")
        
        # Extract the rating from the response (assuming the response provides a number)
        try:
            rating = float(response.text.strip())  # Assume the response is a number
            ratings.append(rating)
        except ValueError:
            st.error(f"Error rating item '{item}'")
            ratings.append(0)  # If rating is invalid, assign a default value
    
    # Calculate the average rating
    average_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Display ratings
    st.subheader("Call Evaluation:")
    for idx, item in enumerate(checklist):
        st.write(f"{item}: {ratings[idx]}")
    
    st.write(f"**Average Rating:** {average_rating}")
    
    # Quality evaluation (based on emotions and nature of call)
    emotions_prompt = f"Evaluate the emotions and nature of the call based on this transcript: {transcription}"
    emotions_response = itsus.generate_content(emotions_prompt)
    
    st.subheader("Call Quality (Emotions and Nature):")
    st.text_area("Evaluation", emotions_response.text, height=150)
    
    # Option to download the transcript and ratings files
    transcript_filename = os.path.splitext(audio_file.name)[0] + "_transcript.txt"
    ratings_filename = os.path.splitext(audio_file.name)[0] + "_ratings.txt"
    
    # Save transcript
    with open(transcript_filename, "w") as file:
        file.write(transcription)
    
    # Save ratings
    with open(ratings_filename, "w") as file:
        file.write(f"Ratings for {audio_file.name}:\n")
        for idx, item in enumerate(checklist):
            file.write(f"{item}: {ratings[idx]}\n")
        file.write(f"\nAverage Rating: {average_rating}\n")
    
    # Provide download links
    with open(transcript_filename, "r") as file:
        st.download_button(
            label="Download Transcript",
            data=file,
            file_name=transcript_filename,
            mime="text/plain"
        )
    
    with open(ratings_filename, "r") as file:
        st.download_button(
            label="Download Ratings & Quality",
            data=file,
            file_name=ratings_filename,
            mime="text/plain"
        )
    
    # Clean up temporary audio file
    os.remove(temp_audio_path)