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
from pathlib import Path

import edge_tts

OUTPUT_DIR = Path("output")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

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

STORY_TEMPLATES = [
    {
        "hook": "THIS PLACE IS REAL, BUT YOU ARE NOT ALLOWED TO GO THERE.",
        "setup": "At first, it sounds like a normal restricted area.",
        "escalation": "Then you realize the rules are not there for privacy.",
        "reveal": "They are there because one mistake can become deadly fast.",
        "twist": "And that is why the warnings are treated like law.",
        "loop": "So if you ever see the sign, do not ignore it.",
        "emotion": "fear",
        "visuals": [
            ["restricted area", "warning sign", "dark road"],
            ["aerial island", "remote location", "ocean"],
            ["abandoned building", "danger sign", "fence"],
            ["storm clouds", "dangerous place", "cinematic"],
            ["no entry sign", "dark cinematic", "security"],
            ["dark road", "warning sign", "night"],
        ],
    },
    {
        "hook": "THIS MYSTERY SHOULD HAVE BEEN SOLVED YEARS AGO.",
        "setup": "Investigators had witnesses, evidence, and a clear timeline.",
        "escalation": "But every answer created a bigger problem.",
        "reveal": "The strangest detail was not what disappeared.",
        "twist": "It was what was left behind.",
        "loop": "That is why people still argue about it today.",
        "emotion": "curiosity",
        "visuals": [
            ["detective board", "mystery", "dark room"],
            ["old documents", "investigation", "papers"],
            ["empty street", "night", "cinematic"],
            ["close up evidence", "flashlight", "dark"],
            ["old newspaper", "secret", "mystery"],
            ["dark room", "files", "investigation"],
        ],
    },
    {
        "hook": "THEY FOUND SOMETHING THAT DID NOT MAKE SENSE.",
        "setup": "The discovery looked ordinary for about five seconds.",
        "escalation": "Then the details started contradicting each other.",
        "reveal": "One part of it should not have been possible.",
        "twist": "And that is what made researchers look twice.",
        "loop": "The weirdest part is that nobody fully agrees on what it means.",
        "emotion": "shock",
        "visuals": [
            ["archaeology discovery", "dark cinematic", "artifact"],
            ["scientist lab", "mysterious object", "close up"],
            ["ancient ruins", "stone", "cinematic"],
            ["old artifact", "museum", "dramatic"],
            ["researchers", "dark lab", "evidence"],
            ["ancient site", "mystery", "sunset"],
        ],
    },
]

def ensure_dirs():
    for folder in [
        "scripts",
        "metadata",
        "trends",
        "premium",
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

    with open(OUTPUT_DIR / "trends" / "trend_scores.json", "w", encoding="utf-8") as f:
        json.dump(rankings, f, indent=2)

    return rankings

def generate_script(topic):
    template = random.choice(STORY_TEMPLATES)
    emotion = template["emotion"]

    scene_texts = [
        template["hook"],
        template["setup"],
        template["escalation"],
        template["reveal"],
        template["twist"],
        template["loop"],
    ]

    roles = [
        "hook",
        "setup",
        "escalation",
        "reveal",
        "twist",
        "loop",
    ]

    base_durations = [
        1.4,
        2.0,
        2.3,
        2.4,
        2.4,
        1.8,
    ]

    scenes = []

    for idx, text in enumerate(scene_texts):
        visual_keywords = template["visuals"][idx]
        scenes.append(
            {
                "scene": idx + 1,
                "text": text,
                "caption_text": wrap_caption(text),
                "base_duration": base_durations[idx],
                "role": roles[idx],
                "keywords": visual_keywords + [topic],
                "emphasis": idx in [0, 3, 4],
                "emotion": emotion if idx != 1 else "curiosity",
                "visual_style": "high contrast cinematic vertical",
            }
        )

    return scenes

def script_to_text(scenes):
    return "\n".join([f"{scene['scene']}. {scene['text']}" for scene in scenes])

def generate_metadata(topic, trend_score):
    return {
        "title": random.choice([
            f"The Strange Truth About {topic.title()}",
            f"This {topic.title()} Story Sounds Fake",
            f"{topic.title()} You Probably Didn't Know",
        ]),
        "description": f"A fast mystery-style short about {topic}.",
        "hashtags": [
            "#strangefacts",
            "#mystery",
            "#weirdhistory",
            "#shorts",
            "#facts",
            "#viral",
        ],
        "platform_fit": ["TikTok", "YouTube Shorts", "Instagram Reels"],
        "trend_score": trend_score,
        "style": "retention-focused documentary short",
        "voice_style": "edge_tts_neural",
        "caption_style": "white cinematic safe-zone captions",
        "thumbnail_focus": topic,
    }

def write_caption_file(index, scene):
    path = OUTPUT_DIR / "captions" / f"video_{index}_scene_{scene['scene']}.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["caption_text"])

    return path

async def generate_narration_async(text, output_path):
    voice = "en-US-ChristopherNeural"

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="-3%",
            pitch="-2Hz",
        )
    except TypeError:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="-3%",
        )

    await communicate.save(str(output_path))

def generate_narration(scene, output_path):
    try:
        asyncio.run(generate_narration_async(scene["text"], output_path))
        return output_path.exists() and output_path.stat().st_size > 0
    except Exception:
        return False

def get_caption_style(scene):
    return {
        "fontcolor": "white",
        "boxcolor": "black@0.52",
        "bordercolor": "black",
    }

def build_visual_query(scene):
    emotion = scene.get("emotion", "mystery")
    keywords = " ".join(scene["keywords"])

    emotion_map = {
        "fear": "danger warning dark cinematic",
        "curiosity": "mysterious evidence cinematic close up",
        "shock": "dramatic discovery intense cinematic",
        "mystery": "unknown mystery cinematic atmosphere",
    }

    return f"{keywords} {emotion_map.get(emotion, 'cinematic mystery')} vertical video"

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
                candidates.append((vertical_bonus + resolution_score, link))

        if not candidates:
            return False

        candidates.sort(reverse=True)
        video_url = candidates[0][1]

        download = requests.get(video_url, stream=True, timeout=45)

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
    audio_duration = get_duration(audio_path) if has_audio else 0.0

    scene_duration = max(float(scene["base_duration"]), audio_duration + 0.55)

    query = build_visual_query(scene)
    has_video = download_stock_video(query, background_video)

    caption_style = get_caption_style(scene)

    font_size = "64" if scene.get("emphasis") else "58"
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
            "[narration][music]amix=inputs=2:duration=first:dropout_transition=0[aout];"
        )
        map_audio = ["-map", "[aout]"]
    else:
        audio_filter = (
            "[1:a]volume=0.09[aout];"
        )
        map_audio = ["-map", "[aout]"]

    video_filter = (
        "[0:v]"
        "scale=1220:2169:force_original_aspect_ratio=increase,"
        "crop=1080:1920:"
        "x='(iw-1080)/2 + sin(t*0.8)*16':"
        "y='(ih-1920)/2 + cos(t*0.55)*16',"
        "fps=30,"
        "eq=contrast=1.10:saturation=1.08,"
        "drawbox=x=0:y=0:w=1080:h=1920:color=black@0.32:t=fill,"
        "drawbox=x=0:y=0:w=1080:h=1920:color=white@0.10:t=fill:enable='between(mod(t,2.25),0,0.055)',"
        f"drawtext=textfile='{caption_file}':"
        f"fontcolor={caption_style['fontcolor']}:"
        f"fontsize={font_size}:"
        "line_spacing=12:"
        "borderw=8:"
        f"bordercolor={caption_style['bordercolor']}:"
        "box=1:"
        f"boxcolor={caption_style['boxcolor']}:"
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
        "-vf",
        "fps=30,format=yuv420p",
        "-af",
        "aresample=async=1:first_pts=0",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "28",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
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
    with open(OUTPUT_DIR / "debug" / "render_report.json", "w", encoding="utf-8") as f:
        json.dump(all_scenes, f, indent=2)

def cleanup_temp():
    temp_dir = OUTPUT_DIR / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

def run():
    ensure_dirs()

    rankings = save_trend_rankings()
    write_performance_template()

    selected_topics = [item["topic"] for item in rankings[:5]]
    all_scenes = []

    for i, topic in enumerate(selected_topics):
        trend_score = next(item for item in rankings if item["topic"] == topic)

        scenes = generate_script(topic)
        metadata = generate_metadata(topic, trend_score)

        render_video(i + 1, scenes)
        save_content(i + 1, scenes, metadata)

        all_scenes.extend(scenes)

        print(
            f"[autovid] generated video {i + 1}: "
            f"{topic} | score {trend_score['total_score']}"
        )

    save_debug_report(all_scenes)
    cleanup_temp()

if __name__ == "__main__":
    run()
