import http.server
import socketserver

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Custom HTML here
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>File Browser</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                a {{ text-decoration: none; color: #007BFF; }}
                a:hover {{ text-decoration: underline; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ padding: 8px; }}
            </style>
        </head>
        <body>
            <h1>Index of {path}</h1>
            <ul>
                {"".join(f"<li><a href='{name}'><button>{name}</button></a></li>" for name in self.get_files(path))}
            </ul>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def get_files(self, path):
        import os
        return os.listdir(path)

with socketserver.TCPServer(("", 8000), CustomHandler) as httpd:
    print("Serving on port 8000...")
    httpd.serve_forever()
