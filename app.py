# Replace your ENTIRE `app.py` with this

```python
#!/usr/bin/env python3

import os
import json
import csv
import random
import datetime
import subprocess
import requests
import shutil
import asyncio
import textwrap
import re
from pathlib import Path

from openai import OpenAI
from elevenlabs.client import ElevenLabs
import edge_tts

OUTPUT_DIR = Path("output")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY)
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

NICHE_TOPICS = {
    "forbidden places": 98,
    "unsolved mysteries": 97,
    "creepy discoveries": 96,
    "strange history": 94,
    "survival stories": 92,
    "science mysteries": 91,
    "ancient civilizations": 89,
    "dangerous places": 88,
    "bizarre true stories": 86,
    "weird geography": 84,
}


def ensure_dirs():
    for folder in [
        "scripts",
        "metadata",
        "trends",
        "videos",
        "captions",
        "logs",
        "packages",
        "temp",
        "audio",
        "debug",
    ]:
        (OUTPUT_DIR / folder).mkdir(parents=True, exist_ok=True)


def run_cmd(command):
    return subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_duration(path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return float(result.stdout.strip())

    except Exception:
        return 0.0


def wrap_caption(text, width=23):
    lines = textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )

    return "\n".join(lines)


def generate_trend_score(topic):
    base_score = NICHE_TOPICS.get(topic, 70)

    novelty = random.randint(70, 100)
    curiosity = random.randint(75, 100)
    retention = random.randint(70, 100)
    emotional_pull = random.randint(70, 100)

    total = round(
        base_score * 0.35
        + novelty * 0.15
        + curiosity * 0.25
        + retention * 0.15
        + emotional_pull * 0.10
    )

    return {
        "topic": topic,
        "base_score": base_score,
        "novelty_score": novelty,
        "curiosity_score": curiosity,
        "predicted_retention_score": retention,
        "emotional_pull_score": emotional_pull,
        "total_score": total,
    }


def save_trend_rankings():
    rankings = [generate_trend_score(topic) for topic in NICHE_TOPICS]

    rankings.sort(key=lambda x: x["total_score"], reverse=True)

    with open(
        OUTPUT_DIR / "trends" / "trend_scores.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(rankings, f, indent=2)

    return rankings


def generate_cinematic_story(topic):
    prompt = f"""
You are writing an ultra-retention-focused short-form mystery story.

TOPIC:
{topic}

CRITICAL RULES:

- Every line must introduce NEW information.
- NEVER repeat the same emotional point.
- Every scene must escalate.
- Use active language.
- Make the story feel cinematic.
- Use short punchy sentences.
- Create curiosity spikes.
- Add contradiction, danger, mystery, or impossible details.
- Avoid generic vague lines.
- Avoid filler.
- Make viewers constantly think: 'wait what?'

STYLE:

- TikTok mystery documentary
- cinematic
- fast-paced
- suspenseful
- highly visual

OUTPUT FORMAT:

Return EXACTLY 7 short scenes.

Each scene should be:
- 1 sentence
- emotionally escalating
- visually distinct
- concrete
- cinematic

Do NOT label scenes.
Do NOT use bullet points.
Do NOT explain anything.
Only output the 7 scene lines.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write extremely high-retention "
                        "short-form cinematic mystery scripts."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=1.05,
            max_tokens=400,
        )

        content = response.choices[0].message.content.strip()

        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip()
        ]

        cleaned = []

        for line in lines:
            line = re.sub(r"^\d+[\.)-]?\s*", "", line)

            if line:
                cleaned.append(line)

        return cleaned[:7]

    except Exception as e:
        print(f"[story-engine-error] {e}")

        return [
            "Nobody expected the discovery to become dangerous.",
            "Then investigators noticed something impossible.",
            "The evidence contradicted the official explanation.",
            "That was when the situation became much stranger.",
            "Researchers realized the timeline made no sense.",
            "One final detail completely changed the story.",
            "And people still debate what really happened.",
        ]


def generate_script(topic):
    story_lines = generate_cinematic_story(topic)

    scenes = []

    for idx, line in enumerate(story_lines):
        emphasis = idx in [0, 3, 5]

        scenes.append(
            {
                "scene": idx + 1,
                "text": line,
                "caption_text": wrap_caption(line),
                "base_duration": 1.8 if idx == 0 else 2.1,
                "role": "story",
                "keywords": [
                    topic,
                    line,
                    "cinematic",
                    "mystery",
                ],
                "emphasis": emphasis,
                "emotion": "mystery",
                "visual_style": "cinematic dramatic realistic",
            }
        )

    return scenes


def script_to_text(scenes):
    return "\n".join(
        [f"{scene['scene']}. {scene['text']}" for scene in scenes]
    )


def generate_metadata(topic, trend_score):
    return {
        "title": random.choice(
            [
                f"The Strange Truth About {topic.title()}",
                f"This {topic.title()} Story Sounds Fake",
                f"{topic.title()} You Probably Didn't Know",
            ]
        ),
        "description": f"A cinematic mystery short about {topic}.",
        "hashtags": [
            "#mystery",
            "#shorts",
            "#viral",
            "#weirdhistory",
            "#facts",
            "#strangefacts",
        ],
        "platform_fit": [
            "TikTok",
            "YouTube Shorts",
            "Instagram Reels",
        ],
        "trend_score": trend_score,
    }


async def generate_narration_async(text, output_path):
    cleaned = re.sub(r"\s+", " ", text).strip()

    cleaned = cleaned.replace(".", ". ")

    try:
        audio = voice_client.generate(
            text=cleaned,
            voice="Adam",
            model="eleven_multilingual_v2",
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

    except Exception as e:
        print(f"[elevenlabs-error] {e}")

        voices = [
            "en-US-AndrewMultilingualNeural",
            "en-US-ChristopherNeural",
            "en-US-EricNeural",
        ]

        selected_voice = random.choice(voices)

        communicate = edge_tts.Communicate(
            text=cleaned,
            voice=selected_voice,
            rate="-13%",
        )

        await communicate.save(str(output_path))


def generate_narration(scene, output_path):
    try:
        asyncio.run(
            generate_narration_async(
                scene["text"],
                output_path,
            )
        )

        return output_path.exists() and output_path.stat().st_size > 0

    except Exception:
        return False


def write_caption_file(index, scene):
    path = (
        OUTPUT_DIR
        / "captions"
        / f"video_{index}_scene_{scene['scene']}.txt"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["caption_text"])

    return path


def build_visual_query(scene):
    text = scene["text"]

    prompt = f"""
Convert this cinematic mystery scene into a short Pexels search query.

SCENE:
{text}

RULES:
- Make it visually specific.
- Focus on objects, places, environments, and actions.
- Keep it under 10 words.
- Prioritize cinematic footage.
- Avoid abstract concepts.
- Output ONLY the search query.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7,
            max_tokens=30,
        )

        query = response.choices[0].message.content.strip()

        return query

    except Exception:
        return f"{text} cinematic dramatic vertical footage"


def download_stock_video(query, output_path):
    if not PEXELS_API_KEY:
        return False

    headers = {"Authorization": PEXELS_API_KEY}

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={
                "query": query,
                "per_page": 7,
                "orientation": "portrait",
            },
            timeout=20,
        )

        if response.status_code != 200:
            return False

        videos = response.json().get("videos", [])

        if not videos:
            return False

        candidates = []

        for video in videos:
            for file in video.get("video_files", []):
                width = file.get("width", 0)
                height = file.get("height", 0)
                link = file.get("link")

                if not link:
                    continue

                vertical_bonus = 2000 if height >= width else 0
                resolution_score = height + width

                candidates.append(
                    (vertical_bonus + resolution_score, link)
                )

        if not candidates:
            return False

        candidates.sort(reverse=True)

        video_url = candidates[0][1]

        download = requests.get(
            video_url,
            stream=True,
            timeout=45,
        )

        if download.status_code != 200:
            return False

        with open(output_path, "wb") as f:
            shutil.copyfileobj(download.raw, f)

        return output_path.exists() and output_path.stat().st_size > 1000

    except Exception:
        return False


def render_scene(video_index, scene, scene_path):
    caption_file = write_caption_file(video_index, scene)

    background_video = (
        OUTPUT_DIR
        / "temp"
        / f"bg_{video_index}_{scene['scene']}.mp4"
    )

    audio_path = (
        OUTPUT_DIR
        / "audio"
        / f"scene_{video_index}_{scene['scene']}.mp3"
    )

    has_audio = generate_narration(scene, audio_path)

    audio_duration = (
        get_duration(audio_path) if has_audio else 0.0
    )

    scene_duration = max(
        float(scene["base_duration"]),
        audio_duration + 0.55,
    )

    query = build_visual_query(scene)

    print(f"[visual-query] scene {scene['scene']}: {query}")

    has_video = download_stock_video(query, background_video)

    font_size = "60" if scene.get("emphasis") else "54"

    y_position = "h-760" if scene.get("emphasis") else "h-700"

    if has_video:
        video_input = [
            "-stream_loop",
            "-1",
            "-i",
            str(background_video),
        ]

    else:
        video_input = [
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x101820:s=1080x1920:r=30:d={scene_duration}",
        ]

    command = [
        "ffmpeg",
        "-y",
        *video_input,
    ]

    if has_audio:
        command += ["-i", str(audio_path)]

    command += [
        "-f",
        "lavfi",
        "-i",
        f"anoisesrc=color=brown:amplitude=0.010:d={scene_duration}",
    ]

    if has_audio:
        audio_filter = (
            "[1:a]volume=1.30[narration];"
            "[2:a]volume=0.10[music];"
            "[narration][music]"
            "amix=inputs=2:duration=first:dropout_transition=0[aout];"
        )

        map_audio = ["-map", "[aout]"]

    else:
        audio_filter = "[1:a]volume=0.09[aout];"

        map_audio = ["-map", "[aout]"]

    video_filter = (
        "[0:v]"
        "scale=1220:2169:force_original_aspect_ratio=increase,"
        "crop=1080:1920:"
        "x='(iw-1080)/2 + sin(t*1.25)*26':"
        "y='(ih-1920)/2 + cos(t*1.05)*26',"
        "fps=30,"
        "drawbox=x=0:y=0:w=1080:h=1920:"
        "color=white@0.18:t=fill:"
        "enable='between(mod(t,1.8),0,0.035)',"
        "eq=contrast=1.12:saturation=1.10,"
        "drawbox=x=0:y=0:w=1080:h=1920:"
        "color=black@0.32:t=fill,"
        f"drawtext=textfile='{caption_file}':"
        "fontcolor=white:"
        f"fontsize={font_size}:"
        "line_spacing=12:"
        "borderw=8:"
        "bordercolor=black:"
        "box=1:"
        "boxcolor=black@0.52:"
        "boxborderw=28:"
        "fix_bounds=1:"
        "x=(w-text_w)/2:"
        f"y={y_position}"
        "[v];"
    )

    command += [
        "-filter_complex",
        video_filter + audio_filter,
        "-map",
        "[v]",
        *map_audio,
        "-t",
        str(scene_duration),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "27",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-pix_fmt",
        "yuv420p",
        str(scene_path),
    ]

    run_cmd(command)


def render_video(index, scenes):
    temp_dir = OUTPUT_DIR / "temp" / f"video_{index}"

    temp_dir.mkdir(parents=True, exist_ok=True)

    scene_files = []

    for scene in scenes:
        scene_path = temp_dir / f"scene_{scene['scene']}.mp4"

        render_scene(index, scene, scene_path)

        if scene_path.exists() and scene_path.stat().st_size > 1000:
            scene_files.append(scene_path)

    concat_file = temp_dir / "concat.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for scene_file in scene_files:
            f.write(f"file '{scene_file.resolve()}'\n")

    output_path = OUTPUT_DIR / "videos" / f"video_{index}.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-vf",
        "fps=30,format=yuv420p",
        "-af",
        "aresample=async=1:first_pts=0",
        "-c:v",
        "libx264",
        "-preset",
        "faster",
        "-crf",
        "30",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    run_cmd(command)


def save_content(index, scenes, metadata):
    timestamp = datetime.datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    with open(
        OUTPUT_DIR
        / "scripts"
        / f"video_{index}_{timestamp}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(scenes, f, indent=2)

    with open(
        OUTPUT_DIR
        / "metadata"
        / f"video_{index}_{timestamp}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(metadata, f, indent=2)


def write_performance_template():
    path = (
        OUTPUT_DIR
        / "logs"
        / "performance_tracking_template.csv"
    )

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(
            [
                "video_file",
                "topic",
                "platform",
                "views",
                "likes",
                "comments",
                "shares",
                "saves",
                "avg_watch_time",
                "completion_rate",
                "notes",
            ]
        )


def cleanup_temp():
    temp_dir = OUTPUT_DIR / "temp"

    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def run():
    ensure_dirs()

    rankings = save_trend_rankings()

    write_performance_template()

    selected_topics = [
        item["topic"] for item in rankings[:5]
    ]

    for i, topic in enumerate(selected_topics):
        trend_score = next(
            item
            for item in rankings
            if item["topic"] == topic
        )

        scenes = generate_script(topic)

        metadata = generate_metadata(topic, trend_score)

        render_video(i + 1, scenes)

        save_content(i + 1, scenes, metadata)

        print(
            f"[autovid] generated video {i + 1}: "
            f"{topic} | score {trend_score['total_score']}"
        )

    cleanup_temp()


if __name__ == "__main__":
    run()
```

Then commit:

```text
Add cinematic AI story engine and ElevenLabs narration
```

Then run the workflow.
