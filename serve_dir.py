from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
import sys

app = FastAPI()

STATIC_DIR = "/home/aavash/Projects/http-server/static"

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

    html_content += "</div></main><footer><p>Served with FastAPI Directory Server</p></footer></body></html>"
    return html_content

@app.get("/{path:path}", response_class=HTMLResponse)
def serve_path(path: str, request: Request):
    full_path = BASE_DIR / path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if full_path.is_dir():
        # Serve directory listing
        return generate_directory_listing(full_path, request)
    else:
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

    """
    with open(STATIC_DIR / "styles.css", "w") as css_file:
        css_file.write(styles)

write_css()

# Instructions to run
if __name__ == "__main__":
    import uvicorn

    # Parse optional port argument
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")

    uvicorn.run(app, host="0.0.0.0", port=port)
