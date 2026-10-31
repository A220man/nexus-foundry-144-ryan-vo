"""Video rendering service using headless browser (Playwright)."""
import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional
import ffmpeg
from playwright.async_api import async_playwright
from app.models.job import Job, JobStatus
from app.core.config import get_settings


class VideoRenderer:
    """Video rendering service using headless browser (Playwright)."""

    def __init__(self):
        self.settings = get_settings()
        self.output_dir = Path(self.settings.video_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None

    async def _ensure_browser(self):
        """Ensure Playwright browser is launched."""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )

    async def _close_browser(self):
        """Close Playwright browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def render_job(self, job: Job) -> str:
        """
        Render a video from job input using Playwright + ffmpeg.
        
        Returns:
            Path to the rendered video file
        """
        await self._ensure_browser()
        
        output_filename = f"{job.id}.{job.format}"
        output_path = self.output_dir / output_filename
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir) / "frames"
            frame_dir.mkdir()
            
            # Create HTML file with job input
            html_path = Path(tmpdir) / "index.html"
            html_content = self._build_html(job)
            html_path.write_text(html_content)
            
            # Calculate frame parameters
            total_frames = int(job.duration * job.fps)
            frame_interval_ms = 1000 / job.fps
            
            # Launch page and capture frames
            page = await self._browser.new_page(
                viewport={"width": job.width, "height": job.height},
                device_scale_factor=1,
            )
            
            try:
                # Navigate to the HTML file
                await page.goto(html_path.as_uri(), wait_until="networkidle")
                
                # Wait a bit for any initial animations
                await page.wait_for_timeout(500)
                
                # Capture frames
                for frame_num in range(total_frames):
                    frame_path = frame_dir / f"frame_{frame_num:06d}.png"
                    await page.screenshot(path=str(frame_path), full_page=False)
                    
                    # If there's CSS animation, advance time
                    if frame_num < total_frames - 1:
                        await page.wait_for_timeout(frame_interval_ms)
                        
            finally:
                await page.close()
            
            # Encode frames to video using ffmpeg
            await self._encode_video(frame_dir, output_path, job)
        
        return str(output_path)

    def _build_html(self, job: Job) -> str:
        """Build complete HTML document from job input."""
        css = job.input_css or ""
        html_body = job.input_html or "<html><body><h1>No content</h1></body></html>"
        
        # Extract body content if full HTML provided
        import re
        body_match = re.search(r"<body[^>]*>(.*?)</body>", html_body, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
        else:
            body_content = html_body
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Foundry Video</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        {css}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""

    async def _encode_video(self, frame_dir: Path, output_path: Path, job: Job) -> None:
        """Encode frames to video using ffmpeg."""
        frame_pattern = str(frame_dir / "frame_%06d.png")
        
        # Build ffmpeg command
        stream = ffmpeg.input(frame_pattern, framerate=job.fps)
        
        if job.format == "webm":
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec="libvpx-vp9",
                pix_fmt="yuva420p",
                crf=30,
                b="0",
            )
        else:  # mp4
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec="libx264",
                pix_fmt="yuv420p",
                preset="medium",
                crf=23,
            )
        
        # Run ffmpeg asynchronously
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: ffmpeg.run(stream, overwrite_output=True, quiet=True)
        )

    def get_video_info(self, path: Path) -> dict:
        """Get video file metadata (duration, dimensions, codec, etc.)."""
        try:
            probe = ffmpeg.probe(str(path))
            video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)
            if video_stream:
                return {
                    "duration": float(video_stream.get("duration", 0)),
                    "width": video_stream.get("width", 0),
                    "height": video_stream.get("height", 0),
                    "codec": video_stream.get("codec_name", "unknown"),
                    "bitrate": int(video_stream.get("bit_rate", 0)),
                }
        except Exception:
            pass
        return {
            "duration": 0,
            "width": 0,
            "height": 0,
            "codec": "unknown",
            "bitrate": 0,
        }

    async def cleanup(self):
        """Clean up browser resources."""
        await self._close_browser()


# Global instance
video_renderer = VideoRenderer()