# 📁 File Upload API

> **File Processing Service**  
> Upload and process files organized by type in asset directories. Supports both URL downloads and direct file uploads.

## 🔑 Authentication

Get your API secret from [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)

## 📡 Base URL
```
https://public.api.bithuman.ai
```

## 🚀 Endpoints

### Upload File

**`POST /v1/files/upload`**

Upload a file to the system for processing. Files are automatically organized by type in asset directories:
- `assets/image/` - Image files
- `assets/video/` - Video files  
- `assets/audio/` - Audio files
- `assets/docs/` - Document files

**Supports two upload methods:**
1. **URL Upload**: Download file from URL
2. **Direct Upload**: Upload file data directly (base64 encoded)

**Headers:**
```http
Content-Type: application/json
api-secret: YOUR_API_SECRET
```

#### Method 1: URL Upload

**Request Body:**
```json
{
  "file_url": "string (required)",
  "file_type": "string (optional)"
}
```

**Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|----------|
| `file_url` | string | URL of the file to download | `"https://example.com/document.pdf"` |
| `file_type` | string | Type of file (pdf, image, audio, video, auto) | `"pdf"` |

**Example:**
```python
import requests

url = "https://public.api.bithuman.ai/v1/files/upload"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}
payload = {
    "file_url": "https://example.com/presentation.pdf",
    "file_type": "pdf"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

#### Method 2: Direct Upload

**Request Body:**
```json
{
  "file_data": "string (required)",
  "file_name": "string (required)",
  "file_type": "string (optional)"
}
```

**Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|----------|
| `file_data` | string | Base64 encoded file data | `"JVBERi0xLjQKJcOkw7zDtsO..."` |
| `file_name` | string | Original filename | `"document.pdf"` |
| `file_type` | string | Type of file (pdf, image, audio, video, auto) | `"pdf"` |

**Example:**
```python
import requests
import base64

# Read and encode file
with open("document.pdf", "rb") as f:
    file_data = base64.b64encode(f.read()).decode('utf-8')

url = "https://public.api.bithuman.ai/v1/files/upload"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}
payload = {
    "file_data": file_data,
    "file_name": "document.pdf",
    "file_type": "pdf"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

**Response (both methods):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "file_url": "https://storage.supabase.co/assets/docs/20250115_103000_abc12345.pdf",
    "original_source": "https://example.com/document.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "asset_category": "docs",
    "uploaded_at": "2025-01-15T10:30:00Z"
  }
}
```

## 📋 Supported File Types

| Asset Category | File Type | Extensions | MIME Type | Storage Path | Use Case |
|----------------|-----------|------------|-----------|--------------|----------|
| **Images** | Image | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.svg` | `image/*` | `assets/image/` | Agent avatars, visual content |
| **Videos** | Video | `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.mkv` | `video/*` | `assets/video/` | Agent videos, motion content |
| **Audio** | Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a` | `audio/*` | `assets/audio/` | Voice samples, audio content |
| **Documents** | PDF/Docs | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv` | `application/*` | `assets/docs/` | Documents, presentations, data files |

## 🗂️ Asset Organization

Files are automatically organized into the following directory structure:

```
assets/
├── image/          # Image files (jpg, png, gif, etc.)
├── video/          # Video files (mp4, avi, mov, etc.)
├── audio/          # Audio files (mp3, wav, flac, etc.)
└── docs/           # Document files (pdf, doc, txt, etc.)
```

Each file is stored with a timestamp and unique identifier:
- Format: `YYYYMMDD_HHMMSS_XXXXXXXX.ext`
- Example: `20250115_103000_abc12345.pdf`

## 🔧 Error Handling

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API secret)
- `413` - File Too Large
- `415` - Unsupported File Type
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Failed to upload file",
  "code": "INTERNAL_ERROR",
  "details": "File processing failed: Invalid file format"
}
```

## 💡 Use Cases

### URL Upload Use Cases
- **External Content**: Download files from external URLs
- **Cloud Storage**: Upload files from cloud storage services
- **Web Scraping**: Process files found on websites
- **Integration**: Import files from third-party services

### Direct Upload Use Cases
- **Local Files**: Upload files from local storage
- **Form Uploads**: Handle file uploads from web forms
- **Mobile Apps**: Upload files from mobile applications
- **Batch Processing**: Process multiple files programmatically

### General Use Cases
- **Document Processing**: Upload PDFs for agent knowledge base
- **Media Assets**: Upload images, audio, or video for agent customization
- **Content Management**: Store and organize files for agent use
- **Integration**: Prepare files for use with other bitHuman services

## 🔄 Upload Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **URL Upload** | External files, cloud storage | No file size limits, efficient | Requires accessible URL |
| **Direct Upload** | Local files, form uploads | Works with any file source | Limited by request size |

## 📝 Complete Examples

### URL Upload Example
```python
import requests

def upload_from_url(file_url, file_type="auto"):
    url = "https://public.api.bithuman.ai/v1/files/upload"
    headers = {
        "Content-Type": "application/json",
        "api-secret": "YOUR_API_SECRET"
    }
    payload = {
        "file_url": file_url,
        "file_type": file_type
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Upload a PDF from URL
result = upload_from_url("https://example.com/document.pdf", "pdf")
print(f"Uploaded to: {result['data']['file_url']}")
```

### Direct Upload Example
```python
import requests
import base64
import os

def upload_local_file(file_path, file_type="auto"):
    # Read and encode file
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')
    
    url = "https://public.api.bithuman.ai/v1/files/upload"
    headers = {
        "Content-Type": "application/json",
        "api-secret": "YOUR_API_SECRET"
    }
    payload = {
        "file_data": file_data,
        "file_name": os.path.basename(file_path),
        "file_type": file_type
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Upload a local image
result = upload_local_file("avatar.jpg", "image")
print(f"Uploaded to: {result['data']['file_url']}")
```

### Batch Upload Example
```python
import requests
import base64
import os
from pathlib import Path

def batch_upload_files(directory_path):
    results = []
    directory = Path(directory_path)
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                # Read and encode file
                with open(file_path, "rb") as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                url = "https://public.api.bithuman.ai/v1/files/upload"
                headers = {
                    "Content-Type": "application/json",
                    "api-secret": "YOUR_API_SECRET"
                }
                payload = {
                    "file_data": file_data,
                    "file_name": file_path.name,
                    "file_type": "auto"
                }
                
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        "filename": file_path.name,
                        "status": "success",
                        "url": result['data']['file_url']
                    })
                else:
                    results.append({
                        "filename": file_path.name,
                        "status": "error",
                        "error": response.text
                    })
            except Exception as e:
                results.append({
                    "filename": file_path.name,
                    "status": "error",
                    "error": str(e)
                })
    
    return results

# Upload all files in a directory
results = batch_upload_files("./documents")
for result in results:
    print(f"{result['filename']}: {result['status']}")
```

## 🔗 Related APIs

- [Agent Generation API](./agent-generation-api.md) - Create agents with uploaded files
- [Dynamics API](./dynamics-api.md) - Generate agent movements and animations
