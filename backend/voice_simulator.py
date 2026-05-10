import os
import asyncio
import whisper
import edge_tts
from backend.interview_coach import InterviewCoach

class VoiceInterviewSimulator:
    """
    Phase 4: Exceptional Voice-to-Voice Interview Simulator.
    API-ready version for web integration.
    """
    def __init__(self, coach=None):
        print("Loading Whisper Model (base)...")
        # In production, we'd load this once and share it
        self.stt_model = whisper.load_model("base")
        self.coach = coach or InterviewCoach()
        # Andrew is a premium-sounding masculine voice, great for technical authority
        self.voice = "en-US-AndrewNeural"

    async def generate_speech(self, text, output_path):
        """Converts text to speech and saves to a file."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        return output_path

    def transcribe_audio(self, audio_path):
        """Transcribes an uploaded audio file."""
        print(f"Transcribing {audio_path}...")
        result = self.stt_model.transcribe(audio_path)
        return result['text']

    async def process_voice_turn(self, audio_path, job_title, question):
        """
        Processes a single turn: Transcription -> Evaluation -> TTS Response.
        Returns evaluation and the path to the TTS feedback audio.
        """
        # 1. Transcribe
        user_text = self.transcribe_audio(audio_path)
        
        if not user_text.strip():
            return {"error": "No speech detected"}, None

        # 2. Evaluate
        evaluation = await self.coach.evaluate_answer(job_title, question, user_text)
        
        # 3. Generate Audio Feedback
        # Extract total_score safely
        total_score = evaluation.get('total_score', 0)
        feedback = evaluation.get('feedback', '')
        
        feedback_text = f"I gave that answer a {total_score} out of 10. {feedback}"
        signal = evaluation.get('seniority_signal', '')
        if signal:
            feedback_text += f" Pro tip: {signal}"
            
        tts_filename = f"feedback_{os.path.basename(audio_path)}.mp3"
        # Ensure data directory exists
        os.makedirs("data/audio", exist_ok=True)
        tts_path = os.path.join("data", "audio", tts_filename)
        await self.generate_speech(feedback_text, tts_path)
        
        return evaluation, tts_path
