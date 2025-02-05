#!/home/aavash/Projects/http-server/env/bin/python

import argparse
import aiofiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import sys
import asyncio
import subprocess
import ffmpeg


app = FastAPI()

STATIC_DIR = Path("/home/aavash/Projects/http-server/static")

# Mount static files for icons and styles
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

BASE_DIR = Path(os.getcwd()).resolve()

# Helper function to generate directory listing
def get_file_icon(file: Path):
    if file.is_dir():
        return "folder.png"
    ext = file.suffix.lower()
    return {
        ".txt": "text.png",
        ".pdf": "pdf.png",
        ".py": "python.png",
        ".jpg": "image.png",
        ".jpeg": "image.png",
        ".png": "image.png",
        ".gif": "image.png",
        ".zip": "archive.png",
        ".tar": "archive.png",
        ".gz": "archive.png",
        ".mp3": "audio.png",
        ".wav": "audio.png",
        ".mp4": "video.png",
        ".mkv": "video.png",
        ".html": "html.png",
        ".css": "css.png",
        ".js": "javascript.png",
    }.get(ext, "file.png")

def generate_directory_listing(path: Path, request: Request):
    files = list(path.iterdir())
    html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Directory Listing</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <header>
            <h1>Directory Listing for {current_path}</h1>
            <a href="/" class="home-button">
                <img src="/static/icons/home.png" alt="Home" style="width: 30px; height: 30px;">
                <span>Home</span>
            </a>
        </header>
        <main>
            <div class="grid">
    """.format(current_path=request.url.path)

    for file in files:
        icon = get_file_icon(file)
        href = f"{request.url.path.rstrip('/')}/{file.name}"
        html_content += f"""
            <a href="{href}" class="item">
                <img src="/static/icons/{icon}" alt="{file.name}">
                <span>{file.name}</span>
            </a>
        """

    html_content += "</div></main><footer><p>Served with FastAPI Directory Server @Gahararagi-OMEN</p></footer></body></html>"
    return html_content

async def transcode_stream(input_path):
    # Try GPU transcoding first
    try:
        # Fallback to direct stream if file is already MP4
        if input_path.suffix.lower() == '.mp4':
            async with aiofiles.open(input_path, mode='rb') as file:
                while chunk := await file.read(1024*1024):
                    yield chunk
                return
        
        process = (
            ffmpeg
            .input(str(input_path))
            .output(
                'pipe:',
                format='mp4',
                vcodec='h264_nvenc',  # NVIDIA GPU acceleration
                acodec='aac',
                movflags='frag_keyframe+empty_moov',
                preset='p4',  # Faster preset for NVIDIA
                gpu='0'  # Use first GPU
            )
            .overwrite_output()
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
    except ffmpeg.Error:
        
        # Fallback to CPU transcoding if GPU fails
        process = (
            ffmpeg
            .input(str(input_path))
            .output(
                'pipe:',
                format='mp4',
                vcodec='libx264',
                acodec='aac',
                movflags='frag_keyframe+empty_moov',
                preset='ultrafast',
                crf=23
            )
            .overwrite_output()
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
    
    while True:
        chunk = await asyncio.get_event_loop().run_in_executor(None, process.stdout.read, 1024*1024)
        if not chunk:
            break
        yield chunk
    
    process.wait()

def generate_video_player(file_path: Path):

    video_url = str(file_path.relative_to(BASE_DIR))
    video_ext = file_path.suffix.lower()
    src = f'/stream/{video_url}'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{file_path.name}</title>
        <link rel="stylesheet" href="/static/styles.css">
        <link href="https://cdn.plyr.io/3.7.8/plyr.css" rel="stylesheet" />
        <style>
            .video-container {{
                max-width: 1280px;
                margin: 0 auto;
                --plyr-color-main: #815ffd;
                align-items: center;
                justify-content:center;
                display: flex;
            }}
            .plyr {{
                height: auto !important;
                width: 75% !important;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Now Playing: {file_path.name}</h1>
            <a href="/" class="home-button">
                <img src="/static/icons/home.png" alt="Home" style="width: 30px; height: 30px;">
                <span>Home</span>
            </a>
        </header>
        <main>
            <div class="video-container">
                <video 
                    id="player" 
                    class="plyr-video"
                    playsinline 
                    controls
                    crossorigin
                >
                    <source src="{src}" type="video/mp4">
                </video>
            </div>
            <header>
                <a href="/download/{video_url}" class="home-button">
                    <img src="/static/icons/download.png" alt="Download" style="width: 30px; height: 30px;">
                    <span>Download</span>
                </a>
            </header>

        </main>
        <footer>
            <p>Served with FastAPI Directory Server @Gahararagi-OMEN</p>
        </footer>
        <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const player = new Plyr('#player', {{
                    controls: [
                        'play-large',
                        'restart',
                        'rewind',
                        'play',
                        'fast-forward',
                        'progress',
                        'current-time',
                        'duration',
                        'mute',
                        'volume',
                        'captions',
                        'settings',
                        'pip',
                        'airplay',
                        'fullscreen'
                    ],
                    keyboard: {{ focused: true, global: true }},
                    tooltips: {{ controls: true, seek: true }},
                    seekTime: 10,
                    quality: {{
                        default: 'auto',
                        options: ['auto', '4k', '1080p', '720p', '480p', '360p']
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/stream/{path:path}")
async def stream_video_route(path: str):
    full_path = BASE_DIR / path
    if not full_path.exists():
        raise HTTPException(status_code=404)
    
    return StreamingResponse(
        transcode_stream(full_path),
        media_type="video/mp4"
    )

@app.get("/download/{path:path}")
async def download_file(path: str):
    full_path = BASE_DIR / path
    if not full_path.exists():
        raise HTTPException(status_code=404)
    
    return FileResponse(full_path)

@app.get("/{path:path}", response_class=HTMLResponse)
def serve_path(path: str, request: Request):
    full_path = BASE_DIR / path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if full_path.is_dir():
        # Serve directory listing
        return generate_directory_listing(full_path, request)
    else:
        if full_path.suffix.lower() in [".mp4", ".mkv",".avi",".mov",".wmv"]:
            # return HTMLResponse(content=generate_video_player(full_path), status_code=200)
            return generate_video_player(full_path)
        # Serve file directly
        return FileResponse(full_path)

# Set up static files directory if it doesn't exist
# STATIC_DIR = BASE_DIR / "static"
ICONS_DIR = STATIC_DIR / "icons"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir()

if not ICONS_DIR.exists():
    ICONS_DIR.mkdir()
    
    # Save placeholder icons (replace these with real images)
    for icon_name in ["folder.png", "file.png", "text.png", "pdf.png", "python.png", "image.png", "archive.png", "audio.png", "video.png", "html.png", "css.png", "javascript.png", "home.png"]:
        with open(ICONS_DIR / icon_name, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # Example placeholder content

# Save CSS for styling
def write_css():
    styles = """
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        background-color: #f9f9f9;
        color: #333;
    }

    header {
        text-align: center;
        margin-bottom: 20px;
    }

    header h1 {
        font-size: 1.8em;
        color: #555;
    }

    .home-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        color: #333;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #fff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-top: 10px;
    }

    .home-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    .home-button img {
        max-width: 24px; /* Adjust size of the home icon */
        height: auto;
        margin-right: 8px;
    }

    .home-button span {
        font-size: 0.9em;
        color: #555;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 20px;
        padding: 10px;
    }

    .item {
        text-align: center;
        text-decoration: none;
        color: #333;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #fff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .item:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    .item img {
        max-width: 80px;
        height: auto;
        display: block;
        margin: 0 auto 10px;
    }

    .item span {
        word-wrap: break-word;
        font-size: 0.9em;
        color: #555;
    }

    footer {
        text-align: center;
        margin-top: 30px;
        font-size: 0.8em;
        color: #aaa;
    }
    
    .gogo{
        color: #815ffd;
        align-items: center;
        align-self: center;
        align-content: center;
    }

    """
    with open(STATIC_DIR / "styles.css", "w") as css_file:
        css_file.write(styles)

write_css()

# Instructions to run
if __name__ == "__main__":
    import uvicorn
    
    parser = argparse.ArgumentParser(description='FastAPI Directory Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--dir', type=str, default=os.getcwd(), help='Directory path to serve')
    
    args = parser.parse_args()
    
    # Set the global BASE_DIR
    BASE_DIR = Path(args.dir).resolve()
    
    if not BASE_DIR.exists():
        print(f"Error: Directory {BASE_DIR} does not exist")
        sys.exit(1)
        
    print(f"Serving directory: {BASE_DIR}")
    print(f"Server running on port: {args.port}")
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)
