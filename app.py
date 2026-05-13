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
import traceback
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

GENERIC_PHRASES = [
    "something impossible",
    "changed everything",
    "official story",
    "people still debate",
    "nobody expected",
    "one detail",
    "what really happened",
    "the truth shocked",
    "mysterious event",
    "investigators discovered",
]

BANNED_VAGUE_WORDS = [
    "something",
    "someone",
    "somebody",
    "thing",
    "situation",
]


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
    return {
        "topic": topic,
        "total_score": NICHE_TOPICS.get(topic, 70),
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


def validate_story(scenes):
    if len(scenes) < 7:
        raise Exception(
            f"Story has insufficient scenes: {len(scenes)}"
        )

    full_text = " ".join(
        [scene["caption"] for scene in scenes]
    ).lower()

    generic_hits = 0

    for phrase in GENERIC_PHRASES:
        if phrase.lower() in full_text:
            generic_hits += 1

    if generic_hits >= 2:
        raise Exception(
            f"Story too generic. Hits: {generic_hits}"
        )

    vague_hits = 0

    for word in BANNED_VAGUE_WORDS:
        vague_hits += full_text.count(word)

    if vague_hits >= 10:
        raise Exception(
            f"Story too vague. Vague count: {vague_hits}"
        )

    unique_lines = len(
        set(scene["caption"].lower() for scene in scenes)
    )

    if unique_lines < 7:
        raise Exception("Duplicate scene lines detected.")

    concrete_nouns = [
        "door",
        "island",
        "camera",
        "forest",
        "city",
        "room",
        "scientist",
        "tunnel",
        "mountain",
        "document",
        "signal",
        "ocean",
        "facility",
        "map",
        "building",
    ]

    noun_hits = 0

    for noun in concrete_nouns:
        if noun in full_text:
            noun_hits += 1

    if noun_hits < 2:
        raise Exception(
            "Story lacks concrete visual details."
        )


def generate_cinematic_story(topic):
    prompt = f"""
You are writing a REAL cinematic short-form mystery story.

TOPIC:
{topic}

ABSOLUTE RULES:

- Every scene MUST introduce NEW information.
- The story MUST progress logically.
- Every scene MUST escalate tension.
- Use SPECIFIC physical details.
- Use named locations, objects, evidence, or discoveries.
- Make scenes visually distinct.
- Avoid generic suspense language.
- Avoid filler.
- Avoid repetition.
- Make it feel like a real documentary.
- Every scene must contain at least one concrete noun.

DO NOT USE:
- "something impossible"
- "changed everything"
- "nobody expected"
- "what really happened"
- "people still debate"
- vague suspense filler

OUTPUT FORMAT:

Return ONLY valid JSON.

Example format:

[
  {{
    "caption": "A diver found a locked steel hatch beneath the ice.",
    "visual_query": "underwater steel hatch diver"
  }}
]

Return EXACTLY 7 scenes.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create cinematic, concrete, "
                        "high-retention mystery stories."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=1.1,
            max_tokens=900,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()

        print("\n[OPENAI RAW STORY OUTPUT]")
        print(content)
        print()

        parsed = json.loads(content)

        if isinstance(parsed, dict):
            if "scenes" in parsed:
                scenes = parsed["scenes"]
            else:
                scenes = list(parsed.values())[0]
        else:
            scenes = parsed

        validate_story(scenes)

        print("[FINAL STORY]")

        for idx, scene in enumerate(scenes):
            print(f"{idx+1}. {scene['caption']}")

        return scenes[:7]

    except Exception as e:
        print("[story-engine-error]")
        print(str(e))
        traceback.print_exc()
        raise


def generate_script(topic):
    story_lines = generate_cinematic_story(topic)

    scenes = []

    for idx, line in enumerate(story_lines):
        emphasis = idx in [0, 3, 5]

        scenes.append(
            {
                "scene": idx + 1,
                "text": line["caption"],
                "caption_text": wrap_caption(
                    line["caption"]
                ),
                "visual_query": line["visual_query"],
                "base_duration": (
                    1.9 if idx == 0 else 2.25
                ),
                "emphasis": emphasis,
            }
        )

    return scenes


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
        "trend_score": trend_score,
    }


async def generate_narration_async(text, output_path):
    cleaned = re.sub(r"\s+", " ", text).strip()

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

        communicate = edge_tts.Communicate(
            text=cleaned,
            voice="en-US-AndrewMultilingualNeural",
            rate="-10%",
        )

        await communicate.save(str(output_path))


def generate_narration(scene, output_path):
    asyncio.run(
        generate_narration_async(
            scene["text"],
            output_path,
        )
    )

    return output_path.exists()


def write_caption_file(index, scene):
    path = (
        OUTPUT_DIR
        / "captions"
        / f"video_{index}_scene_{scene['scene']}.txt"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["caption_text"])

    return path


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

        return output_path.exists()

    except Exception:
        return False


def render_scene(video_index, scene, scene_path):
    caption_file = write_caption_file(
        video_index,
        scene,
    )

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

    generate_narration(scene, audio_path)

    audio_duration = get_duration(audio_path)

    scene_duration = max(
        float(scene["base_duration"]),
        audio_duration + 0.55,
    )

    query = scene["visual_query"]

    print(
        f"[visual-query] scene "
        f"{scene['scene']}: {query}"
    )

    has_video = download_stock_video(
        query,
        background_video,
    )

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
            (
                f"color=c=0x101820:"
                f"s=1080x1920:r=30:d={scene_duration}"
            ),
        ]

    command = [
        "ffmpeg",
        "-y",
        *video_input,
        "-i",
        str(audio_path),
    ]

    video_filter = (
        "[0:v]"
        "scale=1220:2169:"
        "force_original_aspect_ratio=increase,"
        "crop=1080:1920:"
        "x='(iw-1080)/2 + sin(t*1.25)*26':"
        "y='(ih-1920)/2 + cos(t*1.05)*26',"
        "fps=30,"
        "eq=contrast=1.12:saturation=1.10,"
        "drawbox=x=0:y=0:w=1080:h=1920:"
        "color=black@0.28:t=fill,"
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
        "[v]"
    )

    command += [
        "-filter_complex",
        video_filter,
        "-map",
        "[v]",
        "-map",
        "1:a",
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
        scene_path = (
            temp_dir
            / f"scene_{scene['scene']}.mp4"
        )

        render_scene(index, scene, scene_path)

        if (
            scene_path.exists()
            and scene_path.stat().st_size > 1000
        ):
            scene_files.append(scene_path)

    concat_file = temp_dir / "concat.txt"

    with open(
        concat_file,
        "w",
        encoding="utf-8",
    ) as f:
        for scene_file in scene_files:
            f.write(
                f"file '{scene_file.resolve()}'\n"
            )

    output_path = (
        OUTPUT_DIR
        / "videos"
        / f"video_{index}.mp4"
    )

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

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
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
        rankings[0]["topic"]
    ]

    for i, topic in enumerate(selected_topics):
        trend_score = next(
            item
            for item in rankings
            if item["topic"] == topic
        )

        scenes = generate_script(topic)

        metadata = generate_metadata(
            topic,
            trend_score,
        )

        render_video(i + 1, scenes)

        save_content(
            i + 1,
            scenes,
            metadata,
        )

        print(
            f"[autovid] generated video {i + 1}: "
            f"{topic}"
        )

    cleanup_temp()


if __name__ == "__main__":
    run()
