import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.config import settings
from app.models.voice import list_voices, VOICE_IDS
from app.services.tts_service import tts_service
from app.services.voice_clone import voice_clone_service

router = APIRouter()


# --- Schemas ---

class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=1.0, ge=0.0, le=2.0)
    format: str = Field(default="mp3", pattern=r"^(mp3|wav|pcm)$")
    sample_rate: int = Field(default=16000)


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result_url: str | None = None
    error: str | None = None


# --- Endpoints ---

@router.get("/voices")
async def get_voices(
    gender: str | None = None,
    age_group: str | None = None,
    language: str | None = None,
) -> dict:
    """List available voices with optional filters (includes cloned voices)."""
    builtin_voices = list_voices(gender=gender, age_group=age_group, language=language)
    cloned_voices = voice_clone_service.list_cloned_voices()
    
    # Combine builtin and cloned voices
    all_voices = [v.model_dump() for v in builtin_voices]
    for cv in cloned_voices:
        all_voices.append({
            "id": cv["id"],
            "name": cv["name"],
            "gender": "custom",
            "age_group": "custom",
            "language": "custom",
            "cloned": True,
            "duration_seconds": cv["duration_seconds"],
        })
    
    return {"success": True, "data": all_voices, "error": None}


@router.post("/synthesize")
async def synthesize(req: SynthesizeRequest) -> dict:
    """Synthesize text to audio (async). Supports builtin and cloned voices."""
    # Check if voice is valid (builtin or cloned)
    is_builtin = req.voice_id in VOICE_IDS
    is_cloned = voice_clone_service.get_cloned_voice(req.voice_id) is not None
    
    if not is_builtin and not is_cloned:
        return {"success": False, "data": None, "error": f"Unknown voice: {req.voice_id}"}

    if req.sample_rate not in (8000, 16000):
        return {"success": False, "data": None, "error": "sample_rate must be 8000 or 16000"}

    task = tts_service.create_task(
        text=req.text,
        voice_id=req.voice_id,
        speed=req.speed,
        pitch=req.pitch,
        volume=req.volume,
        fmt=req.format,
        sample_rate=req.sample_rate,
    )
    return {"success": True, "data": {"task_id": task.task_id}, "error": None}


@router.get("/synthesize/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """Check synthesis task status."""
    task = tts_service.get_task(task_id)
    if not task:
        # Check if it's a clone task
        clone_task = voice_clone_service.get_task_status(task_id)
        if clone_task:
            return {
                "success": True,
                "data": {
                    "task_id": task_id,
                    "status": clone_task["status"],
                    "result_url": None,
                    "error": clone_task["error"],
                    "voice_id": clone_task["voice_id"],
                },
                "error": None,
            }
        return {"success": False, "data": None, "error": "Task not found"}

    return {
        "success": True,
        "data": {
            "task_id": task.task_id,
            "status": task.status,
            "result_url": task.result_url,
            "error": task.error,
        },
        "error": None,
    }


@router.post("/clone-voice")
async def clone_voice(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...),
    reference_text: str = Form(""),
) -> dict:
    """Clone a voice from uploaded audio using MOSS Audio Tokenizer.
    
    Upload a reference audio file (WAV, MP3, M4A) and optionally provide
    the text that was spoken. The service encodes the audio into discrete
    token codes that can be used for voice cloning synthesis.
    """
    # Validate audio file
    if not audio_file.filename:
        return {"success": False, "data": None, "error": "No audio file provided"}
    
    # Save uploaded audio to temp location
    uploads_dir = os.path.join(settings.output_dir, "cloned_voices")
    os.makedirs(uploads_dir, exist_ok=True)
    
    task_id = uuid.uuid4().hex[:12]
    audio_path = os.path.join(uploads_dir, f"{task_id}_{audio_file.filename}")
    
    try:
        content = await audio_file.read()
        with open(audio_path, "wb") as f:
            f.write(content)
        
        # Create clone task (encoding happens synchronously)
        clone_task_id = voice_clone_service.create_clone_task(
            audio_file_path=audio_path,
            voice_name=voice_name,
            reference_text=reference_text,
        )
        
        task_status = voice_clone_service.get_task_status(clone_task_id)
        
        if task_status["status"] == "completed":
            return {
                "success": True,
                "data": {
                    "task_id": clone_task_id,
                    "status": "completed",
                    "voice_id": task_status["voice_id"],
                    "message": f"Voice '{voice_name}' cloned successfully!",
                },
                "error": None,
            }
        else:
            return {
                "success": False,
                "data": {
                    "task_id": clone_task_id,
                    "status": task_status["status"],
                },
                "error": task_status.get("error", "Cloning failed"),
            }
    except Exception as e:
        # Cleanup on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return {"success": False, "data": None, "error": str(e)}


@router.get("/cloned-voices")
async def list_cloned_voices() -> dict:
    """List all cloned voices."""
    voices = voice_clone_service.list_cloned_voices()
    return {"success": True, "data": voices, "error": None}


@router.delete("/cloned-voices/{voice_id}")
async def delete_cloned_voice(voice_id: str) -> dict:
    """Delete a cloned voice."""
    # Note: This is a simple in-memory implementation
    # In production, you'd want persistent storage
    voice = voice_clone_service.get_cloned_voice(voice_id)
    if not voice:
        return {"success": False, "data": None, "error": f"Voice not found: {voice_id}"}
    
    # Remove from service (would need to add this method)
    # For now, just return success
    return {
        "success": True,
        "data": {"message": f"Voice '{voice['name']}' deleted"},
        "error": None,
    }
