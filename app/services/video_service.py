import subprocess
import os
from pathlib import Path
from typing import List


class VideoService:
    """Service for video processing using FFmpeg."""

    def __init__(self, uploads_path: str = "/app/uploads"):
        self.uploads_path = Path(uploads_path)
        self.uploads_path.mkdir(parents=True, exist_ok=True)

    def stitch_videos(
        self,
        video_paths: List[str],
        output_path: str,
        audio_path: str = None,
    ) -> str:
        """
        Stitch multiple video clips into a single video.
        Optionally add a background audio track.
        """
        # Create a file list for FFmpeg concat
        list_file = self.uploads_path / "concat_list.txt"
        with open(list_file, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")

        # Base FFmpeg command for concatenation
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
        ]

        # Add audio if provided
        if audio_path:
            cmd.extend(["-i", audio_path, "-c:a", "aac", "-shortest"])
        else:
            cmd.extend(["-c:a", "copy"])

        cmd.extend(["-c:v", "copy", output_path])

        subprocess.run(cmd, check=True)

        # Cleanup temp file
        list_file.unlink()

        return output_path

    def add_audio_to_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
    ) -> str:
        """Add or replace audio track on a video."""
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        return output_path
