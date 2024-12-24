# Simple HTTP Server with User-Friendly UI

## Main Purpose
File Sharing

## Implementation
**Framework:** FastAPI

## Usage as a Binary
For Linux systems:

1. Set up the virtual environment and update its path in `serve_dir`.
2. Copy the `serve_dir` binary to `/usr/local/bin/`:
   ```bash
   sudo cp serve_dir /usr/local/bin/
   ```
3. Make the binary executable:
   ```bash
   chmod +x /usr/local/bin/serve_dir
   ```
4. **Important:** Update the path to the static files to the actual full path of the static files on your system.

Open the code editor of your choice to update the serve_dir file. For example:
```bash
   nano serve_dir
```
Update this line:
```python
    STATIC_DIR = Path("/absolute/path/to/static/files")
```

## Use Cases

### **No Arguments**

#### Command:
```bash
python serve_dir.py
```
**OR** (if set up as a binary):
```bash
serve_dir
```
#### Result:
Hosts the current directory on port `8000`.

---

### **With Arguments**

#### Command:
```bash
python serve_dir.py --dir /path/you/want/to/host --port port_number
```
**OR** (if set up as a binary):
```bash
serve_dir --dir /path/you/want/to/host --port port_number
```
#### Result:
Hosts the specified directory on the specified port.

---

## Example Commands

### Hosting Current Directory (Default Port):
```bash
serve_dir
```

### Hosting a Specific Directory:
```bash
serve_dir --dir /home/user/shared --port 8080
```

---

## Notes
- Ensure the path to the static files (`STATIC_DIR`) is correctly updated in the script before execution.
- This setup is ideal for sharing files locally or within a network, offering a user-friendly interface powered by FastAPI.

---

Enjoy beautiful file sharing with `serve_dir`!

