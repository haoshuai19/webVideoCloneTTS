from pydantic import BaseModel


class Voice(BaseModel):
    """Voice definition."""

    id: str
    name: str
    gender: str  # male/female
    age_group: str  # child/young/middle/old
    language: str  # zh/en/mixed


# Voice definitions matching manifest voices
VOICES = [
    Voice(id="xiaoyuan", name="小媛", gender="female", age_group="young", language="zh"),
    Voice(id="xiaobei", name="小贝", gender="female", age_group="young", language="zh"),
    Voice(id="xiaogang", name="小刚", gender="male", age_group="young", language="zh"),
    Voice(id="xiaoxue", name="小雪", gender="female", age_group="middle", language="zh"),
    Voice(id="laoli", name="老李", gender="male", age_group="old", language="zh"),
    Voice(id="xiaoming", name="小明", gender="male", age_group="child", language="zh"),
]

VOICE_IDS = {v.id for v in VOICES}


def list_voices(
    gender: str | None = None,
    age_group: str | None = None,
    language: str | None = None,
) -> list[Voice]:
    """List voices with optional filters."""
    voices = VOICES
    if gender:
        voices = [v for v in voices if v.gender == gender]
    if age_group:
        voices = [v for v in voices if v.age_group == age_group]
    if language:
        voices = [v for v in voices if v.language == language]
    return voices


def get_voice(voice_id: str) -> Voice | None:
    """Get voice by ID."""
    for v in VOICES:
        if v.id == voice_id:
            return v
    return None
