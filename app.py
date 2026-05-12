#!/usr/bin/env python3

import os
import json
import csv
import random
import datetime
import subprocess
import requests
import shutil
from pathlib import Path

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
    {
        "text": "THIS SOUNDS FAKE, BUT IT'S REAL.",
        "strength": 96
    },
    {
        "text": "THIS MYSTERY STILL HASN'T BEEN SOLVED.",
        "strength": 99
    },
    {
        "text": "THIS PLACE SHOULD NOT EXIST.",
        "strength": 95
    },
    {
        "text": "THIS DISCOVERY TERRIFIED RESEARCHERS.",
        "strength": 94
    },
    {
        "text": "NOBODY EXPECTED THIS TO HAPPEN.",
        "strength": 92
    },
]

NARRATIVE_PATTERNS = [
    {
        "type": "forbidden_truth",
        "middle": "What they discovered was never meant to be public.",
        "ending": "And people still debate what really happened.",
        "emotion": "fear"
    },
    {
        "type": "unsolved_mystery",
        "middle": "Researchers still cannot explain the evidence.",
        "ending": "And the mystery remains unsolved today.",
        "emotion": "curiosity"
    },
    {
        "type": "terrifying_discovery",
        "middle": "The discovery shocked everyone involved.",
        "ending": "And nobody fully understands it.",
        "emotion": "shock"
    },
]

BACKGROUND_COLORS = [
    "0x050505",
    "0x0b0b12",
    "0x101018",
    "0x080d14",
    "0x120909",
    "0x0b1110",
    "0x161616",
    "0x1b0f0f",
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
    ]:
        (OUTPUT_DIR / folder).mkdir(
            parents=True,
            exist_ok=True
        )

def generate_hook():
    weighted = []

    for hook in HOOK_TEMPLATES:
        weighted.extend(
            [hook["text"]] * hook["strength"]
        )

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
    rankings = [
        generate_trend_score(topic)
        for topic in NICHE_TOPICS
    ]

    rankings.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    with open(
        OUTPUT_DIR / "trends" / "trend_scores.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(rankings, f, indent=2)

    return rankings

def generate_script(topic, hook):
    pattern = random.choice(
        NARRATIVE_PATTERNS
    )

    return [
        {
            "scene": 1,
            "text": hook,
            "duration": 2,
            "role": "hook",
            "keywords": [topic, "mystery"],
            "emphasis": True,
            "emotion": pattern["emotion"],
            "visual_style": "dark_cinematic",
            "transition_style": "shock_cut"
        },
        {
            "scene": 2,
            "text": (
                f"Most people have never "
                f"heard about {topic}."
            ),
            "duration": 3,
            "role": "setup",
            "keywords": [topic],
            "emphasis": False,
            "emotion": "curiosity",
            "visual_style": "dark_cinematic",
            "transition_style": "fade"
        },
        {
            "scene": 3,
            "text": pattern["middle"],
            "duration": 4,
            "role": "middle",
            "keywords": [
                "dark",
                "truth",
                topic
            ],
            "emphasis": True,
            "emotion": pattern["emotion"],
            "visual_style": "dark_cinematic",
            "transition_style": "impact"
        },
        {
            "scene": 4,
            "text": pattern["ending"],
            "duration": 5,
            "role": "payoff",
            "keywords": [
                "unknown",
                "creepy",
                topic
            ],
            "emphasis": True,
            "emotion": "fear",
            "visual_style": "dark_cinematic",
            "transition_style": "slow_fade"
        },
        {
            "scene": 5,
            "text": (
                "FOLLOW FOR MORE "
                "STRANGE STORIES."
            ),
            "duration": 2,
            "role": "cta",
            "keywords": [
                "follow",
                "cta"
            ],
            "emphasis": False,
            "emotion": "engagement",
            "visual_style": "clean",
            "transition_style": "fade"
        },
    ]

def script_to_text(scenes):
    return "\n".join(
        [
            f"{scene['scene']}. "
            f"{scene['text']}"
            for scene in scenes
        ]
    )

def generate_metadata(topic, trend_score):
    title_options = [
        (
            f"{topic.title()} "
            f"You Probably Didn't Know"
        ),
        (
            f"The Strange Truth About "
            f"{topic.title()}"
        ),
        (
            f"This {topic.title()} "
            f"Story Sounds Fake"
        ),
    ]

    return {
        "title": random.choice(title_options),
        "description": (
            f"A short mystery-style "
            f"story about {topic}."
        ),
        "hashtags": [
            "#strangefacts",
            "#weirdhistory",
            "#mystery",
            "#shorts",
            "#facts",
            "#viral",
        ],
        "platform_fit": [
            "TikTok",
            "YouTube Shorts",
            "Instagram Reels"
        ],
        "trend_score": trend_score,
        "predicted_hook_strength":
            random.randint(80, 99),
        "predicted_rewatchability":
            random.randint(75, 98),
        "recommended_length_seconds": 16,
        "style":
            "dark documentary + "
            "fast curiosity pacing",
        "voice_style":
            "dark_documentary",
        "narration_priority":
            "high",
        "caption_style":
            "cinematic_large",
        "soundtrack_style":
            "dark_ambient_tension",
        "thumbnail_focus":
            topic,
    }

def write_caption_file(index, scene):
    path = (
        OUTPUT_DIR
        / "captions"
        / (
            f"video_{index}_"
            f"scene_{scene['scene']}.txt"
        )
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(scene["text"])

    return path

def download_stock_video(
    query,
    output_path
):
    if not PEXELS_API_KEY:
        return False

    headers = {
        "Authorization":
            PEXELS_API_KEY
    }

    url = (
        "https://api.pexels.com/videos/search"
        f"?query={query}&per_page=1"
    )

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        data = response.json()

        videos = data.get(
            "videos",
            []
        )

        if not videos:
            return False

        video_files = videos[0].get(
            "video_files",
            []
        )

        if not video_files:
            return False

        best_video = sorted(
            video_files,
            key=lambda x:
                x.get("width", 0),
            reverse=True
        )[0]

        video_url = best_video["link"]

        r = requests.get(
            video_url,
            stream=True,
            timeout=30
        )

        with open(
            output_path,
            "wb"
        ) as f:
            shutil.copyfileobj(
                r.raw,
                f
            )

        return True

    except Exception:
        return False

def render_scene(
    video_index,
    scene,
    scene_path
):
    caption_file = write_caption_file(
        video_index,
        scene
    )

    color = random.choice(
        BACKGROUND_COLORS
    )

    background_video = (
        OUTPUT_DIR
        / "temp"
        / (
            f"bg_{video_index}_"
            f"{scene['scene']}.mp4"
        )
    )

    query = " ".join(
        scene["keywords"]
    )

    has_video = download_stock_video(
        query,
        background_video
    )

    font_size = (
        "84"
        if scene.get("emphasis")
        else "68"
    )

    box_opacity = (
        "0.45"
        if scene.get("emphasis")
        else "0.35"
    )

    command = [
        "ffmpeg",
        "-y",

        *(

            [
                "-stream_loop",
                "-1",
                "-i",
                str(background_video),
            ]

            if has_video

            else

            [
                "-f",
                "lavfi",
                "-i",
                (
                    f"color=c={color}:"
                    f"s=1080x1920:"
                    f"d={scene['duration']}"
                ),
            ]

        ),

        "-vf",

        (
            "scale=1200:2133,"
            "crop=1080:1920:"
            "x='(iw-1080)/2 + sin(t*0.3)*20':"
            "y='(ih-1920)/2 + cos(t*0.2)*20',"

            "drawbox="
            "x=0:y=0:w=1080:h=1920:"
            "color=black@0.25:t=fill,"

            f"drawtext="
            f"textfile='{caption_file}':"
            "fontcolor=white:"
            f"fontsize={font_size}:"
            "borderw=6:"
            "bordercolor=black:"
            "box=1:"
            f"boxcolor=black@{box_opacity}:"
            "boxborderw=35:"
            "x=(w-text_w)/2:"
            "y=h-620"
        ),

        "-t",
        str(scene["duration"]),

        "-c:v",
        "libx264",

        "-pix_fmt",
        "yuv420p",

        str(scene_path),
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def render_video(
    index,
    scenes
):
    temp_dir = (
        OUTPUT_DIR
        / "temp"
        / f"video_{index}"
    )

    temp_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    scene_files = []

    for scene in scenes:
        scene_path = (
            temp_dir
            / (
                f"scene_"
                f"{scene['scene']}.mp4"
            )
        )

        render_scene(
            index,
            scene,
            scene_path
        )

        scene_files.append(scene_path)

    concat_file = (
        temp_dir
        / "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:
        for scene_file in scene_files:
            f.write(
                f"file "
                f"'{scene_file.resolve()}'\n"
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
        "-c",
        "copy",
        str(output_path),
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return output_path

def save_package(
    index,
    metadata
):
    package_path = (
        OUTPUT_DIR
        / "packages"
        / (
            f"video_{index}_"
            f"platform_package.json"
        )
    )

    with open(
        package_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {
                "youtube_shorts": {
                    "title":
                        metadata["title"],
                    "description":
                        metadata["description"],
                    "hashtags":
                        metadata["hashtags"],
                },
                "tiktok": {
                    "caption":
                        metadata["title"]
                        + " "
                        + " ".join(
                            metadata["hashtags"]
                        ),
                },
                "instagram_reels": {
                    "caption":
                        metadata["description"]
                        + " "
                        + " ".join(
                            metadata["hashtags"]
                        ),
                },
            },
            f,
            indent=2,
        )

def save_content(
    index,
    scenes,
    metadata
):
    timestamp = (
        datetime.datetime.utcnow()
        .strftime("%Y%m%d_%H%M%S")
    )

    script_json_path = (
        OUTPUT_DIR
        / "scripts"
        / (
            f"video_{index}_"
            f"{timestamp}.json"
        )
    )

    script_txt_path = (
        OUTPUT_DIR
        / "scripts"
        / (
            f"video_{index}_"
            f"{timestamp}.txt"
        )
    )

    metadata_path = (
        OUTPUT_DIR
        / "metadata"
        / (
            f"video_{index}_"
            f"{timestamp}.json"
        )
    )

    with open(
        script_json_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            scenes,
            f,
            indent=2
        )

    with open(
        script_txt_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            script_to_text(scenes)
        )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2
        )

    save_package(
        index,
        metadata
    )

    if (
        metadata["trend_score"]
        ["total_score"]
        >= 90
    ):
        premium_path = (
            OUTPUT_DIR
            / "premium"
            / (
                f"video_{index}_"
                f"{timestamp}.json"
            )
        )

        with open(
            premium_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                {
                    "reason":
                        (
                            "High trend score. "
                            "Consider InVideo "
                            "or Sora enhancement."
                        ),
                    "script_data":
                        scenes,
                    "metadata":
                        metadata
                },
                f,
                indent=2
            )

def write_performance_template():
    path = (
        OUTPUT_DIR
        / "logs"
        / (
            "performance_"
            "tracking_template.csv"
        )
    )

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
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

def run():
    ensure_dirs()

    rankings = save_trend_rankings()

    write_performance_template()

    selected_topics = [
        item["topic"]
        for item in rankings[:5]
    ]

    for i, topic in enumerate(
        selected_topics
    ):
        hook = generate_hook()

        trend_score = next(
            item
            for item in rankings
            if item["topic"] == topic
        )

        scenes = generate_script(
            topic,
            hook
        )

        metadata = generate_metadata(
            topic,
            trend_score
        )

        save_content(
            i + 1,
            scenes,
            metadata
        )

        render_video(
            i + 1,
            scenes
        )

        print(
            f"[autovid] generated "
            f"video {i + 1}: "
            f"{topic} | "
            f"score "
            f"{trend_score['total_score']}"
        )

if __name__ == "__main__":
    run()
