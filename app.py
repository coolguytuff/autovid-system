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
from pathlib import Path

import edge_tts

OUTPUT_DIR = Path("output")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

NICHE_TOPICS = {
    "creepy discoveries": 97,
    "unsolved mysteries": 96,
    "forbidden places": 95,
    "bizarre true stories": 94,
    "science mysteries": 93,
    "survival stories": 91,
    "strange history": 88,
    "ancient civilizations": 86,
    "dangerous places": 84,
    "weird geography": 82,
}

HOOK_TEMPLATES = [
    {"text": "THIS SOUNDS FAKE, BUT IT'S REAL.", "strength": 96},
    {"text": "THIS MYSTERY STILL HASN'T BEEN SOLVED.", "strength": 99},
    {"text": "THIS PLACE SHOULD NOT EXIST.", "strength": 95},
    {"text": "THIS DISCOVERY TERRIFIED RESEARCHERS.", "strength": 94},
    {"text": "NOBODY EXPECTED THIS TO HAPPEN.", "strength": 92},
]

NARRATIVE_PATTERNS = [
    {
        "middle": "What they discovered was never meant to be public.",
        "ending": "And people still debate what really happened.",
        "emotion": "fear",
    },
    {
        "middle": "Researchers still cannot explain the evidence.",
        "ending": "And the mystery remains unsolved today.",
        "emotion": "curiosity",
    },
    {
        "middle": "The discovery shocked everyone involved.",
        "ending": "And nobody fully understands it.",
        "emotion": "shock",
    },
]

def ensure_dirs():
    for folder in [
        "scripts", "metadata", "trends", "premium", "videos",
        "captions", "logs", "packages", "temp", "audio", "debug"
    ]:
        (OUTPUT_DIR / folder).mkdir(parents=True, exist_ok=True)

def run_cmd(command):
    return subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_duration(path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def generate_hook():
    weighted = []
    for hook in HOOK_TEMPLATES:
        weighted.extend([hook["text"]] * hook["strength"])
    return random.choice(weighted)

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

    with open(OUTPUT_DIR / "trends" / "trend_scores.json", "w", encoding="utf-8") as f:
        json.dump(rankings, f, indent=2)

    return rankings

def generate_script(topic, hook):
    pattern = random.choice(NARRATIVE_PATTERNS)

    return [
        {
            "scene": 1,
            "text": hook,
            "base_duration": 1.8,
            "role": "hook",
            "keywords": [topic, "mystery"],
            "emphasis": True,
            "emotion": pattern["emotion"],
            "visual_style": "dark cinematic",
        },
        {
            "scene": 2,
            "text": f"Most people have never heard about {topic}.",
            "base_duration": 3.0,
            "role": "setup",
            "keywords": [topic],
            "emphasis": False,
            "emotion": "curiosity",
            "visual_style": "dark cinematic",
        },
        {
            "scene": 3,
            "text": pattern["middle"],
            "base_duration": 4.0,
            "role": "middle",
            "keywords": ["dark", "truth", topic],
            "emphasis": True,
            "emotion": pattern["emotion"],
            "visual_style": "dark cinematic",
        },
        {
            "scene": 4,
            "text": pattern["ending"],
            "base_duration": 5.0,
            "role": "payoff",
            "keywords": ["unknown", "creepy", topic],
            "emphasis": True,
            "emotion": "fear",
            "visual_style": "dark cinematic",
        },
        {
            "scene": 5,
            "text": "FOLLOW FOR MORE STRANGE STORIES.",
            "base_duration": 1.6,
            "role": "cta",
            "keywords": ["follow", "cta"],
            "emphasis": False,
            "emotion": "engagement",
            "visual_style": "clean cinematic",
        },
    ]

def script_to_text(scenes):
    return "\n".join([f"{scene['scene']}. {scene['text']}" for scene in scenes])

def generate_metadata(topic, trend_score):
    return {
        "title": random.choice([
            f"{topic.title()} You Probably Didn't Know",
            f"The Strange Truth About {topic.title()}",
            f"This {topic.title()} Story Sounds Fake",
        ]),
        "description": f"A short mystery-style story about {topic}.",
        "hashtags": [
            "#strangefacts",
            "#weirdhistory",
            "#mystery",
            "#shorts",
            "#facts",
            "#viral",
        ],
        "platform_fit": ["TikTok", "YouTube Shorts", "Instagram Reels"],
        "trend_score": trend_score,
        "style": "dark documentary + fast curiosity pacing",
        "voice_style": "edge_tts_neural",
        "caption_style": "cinematic_emotional",
        "thumbnail_focus": topic,
    }

def write_caption_file(index, scene):
    path = OUTPUT_DIR / "captions" / f"video_{index}_scene_{scene['scene']}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["text"])
    return path

async def generate_narration_async(text, output_path):
    voice = "en-US-GuyNeural"
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+8%")
    await communicate.save(str(output_path))

def generate_narration(scene, output_path):
    try:
        asyncio.run(generate_narration_async(scene["text"], output_path))
        return output_path.exists() and output_path.stat().st_size > 0
    except Exception:
        return False

def get_caption_style(scene):
    emotion = scene.get("emotion", "mystery")

    styles = {
        "fear": {"fontcolor": "white", "boxcolor": "darkred@0.48"},
        "curiosity": {"fontcolor": "cyan", "boxcolor": "black@0.42"},
        "shock": {"fontcolor": "yellow", "boxcolor": "black@0.50"},
        "mystery": {"fontcolor": "white", "boxcolor": "black@0.38"},
        "engagement": {"fontcolor": "white", "boxcolor": "black@0.40"},
    }

    return styles.get(emotion, styles["mystery"])

def build_visual_query(scene):
    emotion = scene.get("emotion", "mystery")
    style = scene.get("visual_style", "dark cinematic")
    keywords = " ".join(scene["keywords"])

    emotion_map = {
        "fear": "dark abandoned scary cinematic",
        "curiosity": "mysterious discovery cinematic",
        "shock": "dramatic intense cinematic",
        "mystery": "unknown cinematic atmosphere",
        "engagement": "dark cinematic background",
    }

    return f"{keywords} {style} {emotion_map.get(emotion, 'cinematic mystery')}"

def download_stock_video(query, output_path):
    if not PEXELS_API_KEY:
        return False

    headers = {"Authorization": PEXELS_API_KEY}

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": query, "per_page": 5, "orientation": "portrait"},
            timeout=20,
        )

        if response.status_code != 200:
            return False

        data = response.json()
        videos = data.get("videos", [])

        if not videos:
            return False

        candidates = []

        for video in videos:
            for file in video.get("video_files", []):
                width = file.get("width", 0)
                height = file.get("height", 0)
                link = file.get("link")
                if link:
                    vertical_bonus = 1000 if height >= width else 0
                    candidates.append((vertical_bonus + height + width, link))

        if not candidates:
            return False

        candidates.sort(reverse=True)
        video_url = candidates[0][1]

        download = requests.get(video_url, stream=True, timeout=40)
        if download.status_code != 200:
            return False

        with open(output_path, "wb") as f:
            shutil.copyfileobj(download.raw, f)

        return output_path.exists() and output_path.stat().st_size > 1000

    except Exception:
        return False

def render_scene(video_index, scene, scene_path):
    caption_file = write_caption_file(video_index, scene)

    background_video = OUTPUT_DIR / "temp" / f"bg_{video_index}_{scene['scene']}.mp4"
    audio_path = OUTPUT_DIR / "audio" / f"scene_{video_index}_{scene['scene']}.mp3"

    has_audio = generate_narration(scene, audio_path)
    audio_duration = get_duration(audio_path) if has_audio else 0

    scene_duration = max(float(scene["base_duration"]), audio_duration + 0.35)

    query = build_visual_query(scene)
    has_video = download_stock_video(query, background_video)

    caption_style = get_caption_style(scene)
    font_size = "86" if scene.get("emphasis") else "68"

    if has_video:
        video_input = [
            "-stream_loop", "-1",
            "-i", str(background_video),
        ]
    else:
        video_input = [
            "-f", "lavfi",
            "-i", f"testsrc2=s=1080x1920:rate=30:d={scene_duration}",
        ]

    command = [
        "ffmpeg",
        "-y",
        *video_input,
    ]

    if has_audio:
        command += ["-i", str(audio_path)]

    command += [
        "-f", "lavfi",
        "-i", f"anoisesrc=color=pink:amplitude=0.018:d={scene_duration}",
    ]

    if has_audio:
        audio_filter = (
            "[1:a]volume=1.15[narration];"
            "[2:a]volume=0.16[music];"
            "[narration][music]amix=inputs=2:duration=first[aout];"
        )
        map_audio = ["-map", "[aout]"]
    else:
        audio_filter = "[1:a]volume=0.12[aout];"
        map_audio = ["-map", "[aout]"]

    video_filter = (
        "[0:v]"
        "scale=1200:2133:force_original_aspect_ratio=increase,"
        "crop=1080:1920:"
        "x='(iw-1080)/2 + sin(t*0.7)*18':"
        "y='(ih-1920)/2 + cos(t*0.5)*18',"
        "drawbox=x=0:y=0:w=1080:h=1920:color=black@0.34:t=fill,"
        f"drawtext=textfile='{caption_file}':"
        f"fontcolor={caption_style['fontcolor']}:"
        f"fontsize={font_size}:"
        "borderw=7:"
        "bordercolor=black:"
        "box=1:"
        f"boxcolor={caption_style['boxcolor']}:"
        "boxborderw=34:"
        "x=(w-text_w)/2:"
        "y=h-620"
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
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        str(scene_path),
    ]

    run_cmd(command)

    scene["final_duration"] = round(scene_duration, 2)
    scene["used_pexels_footage"] = has_video
    scene["used_narration"] = has_audio
    scene["visual_query"] = query

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
        "-c",
        "copy",
        str(output_path),
    ]

    run_cmd(command)
    return output_path

def save_package(index, metadata):
    package_path = OUTPUT_DIR / "packages" / f"video_{index}_platform_package.json"

    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "youtube_shorts": {
                    "title": metadata["title"],
                    "description": metadata["description"],
                    "hashtags": metadata["hashtags"],
                },
                "tiktok": {
                    "caption": metadata["title"] + " " + " ".join(metadata["hashtags"]),
                },
                "instagram_reels": {
                    "caption": metadata["description"] + " " + " ".join(metadata["hashtags"]),
                },
            },
            f,
            indent=2,
        )

def save_content(index, scenes, metadata):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    with open(OUTPUT_DIR / "scripts" / f"video_{index}_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2)

    with open(OUTPUT_DIR / "scripts" / f"video_{index}_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(script_to_text(scenes))

    with open(OUTPUT_DIR / "metadata" / f"video_{index}_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    save_package(index, metadata)

    if metadata["trend_score"]["total_score"] >= 90:
        with open(OUTPUT_DIR / "premium" / f"video_{index}_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "reason": "High trend score. Consider InVideo or Sora enhancement.",
                    "script_data": scenes,
                    "metadata": metadata,
                },
                f,
                indent=2,
            )

def write_performance_template():
    path = OUTPUT_DIR / "logs" / "performance_tracking_template.csv"

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
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
        ])

def save_debug_report(all_scenes):
    report_path = OUTPUT_DIR / "debug" / "render_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_scenes, f, indent=2)

def run():
    ensure_dirs()
    rankings = save_trend_rankings()
    write_performance_template()

    selected_topics = [item["topic"] for item in rankings[:5]]
    all_scenes = []

    for i, topic in enumerate(selected_topics):
        hook = generate_hook()
        trend_score = next(item for item in rankings if item["topic"] == topic)

        scenes = generate_script(topic, hook)
        metadata = generate_metadata(topic, trend_score)

        render_video(i + 1, scenes)
        save_content(i + 1, scenes, metadata)

        all_scenes.extend(scenes)

        print(f"[autovid] generated video {i + 1}: {topic} | score {trend_score['total_score']}")

    save_debug_report(all_scenes)

if __name__ == "__main__":
    run()
