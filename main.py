from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi.middleware.cors import CORSMiddleware
import re
from urllib.parse import urlparse, parse_qs

app = FastAPI()

# CORS configuration - Option 2 recommended for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as is if it's already an ID."""
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/e\/|youtube\.com\/user\/[^\/]+\/[^\/]+\/|youtube\.com\/[^\/]+\/[^\/]+\/|youtube\.com\/verify_age\?next_url=\/watch%3Fv%3D)([^\"&?\/\s]{11})',
        r'(?:youtube\.com\/shorts\/)([^\"&?\/\s]{11})',
    ]
    
    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # If no patterns match but the string is 11 characters, assume it's already an ID
    if len(url_or_id) == 11:
        return url_or_id
        
    raise ValueError("Could not extract video ID from URL")

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}

@app.get("/transcript/{video_url:path}")
async def get_transcript(video_url: str):
    try:
        # Extract video ID from URL or use as is
        video_id = extract_video_id(video_url)
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format transcript for better readability (optional)
        formatted_transcript = [
            {
                "text": entry["text"],
                "start": entry["start"],
                "duration": entry["duration"]
            }
            for entry in transcript
        ]
        
        return {"transcript": formatted_transcript}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))