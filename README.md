# 🎬 MP4 → AAC Telegram Bot

A lightweight Telegram bot that receives MP4 video files and replies with the extracted audio as an AAC file.

Built with Python + pyTelegramBotAPI + FFmpeg. Designed to be deployed on a VPS via **Dokploy**.

---

## Features

- Accepts MP4 videos sent normally (compressed) or as raw files (uncompressed)
- Extracts audio using FFmpeg at 192kbps AAC quality
- Replies with the `.aac` file directly in chat
- Rejects non-MP4 documents with a friendly warning
- Cleans up temp files after every conversion
- Minimal image: `python:3.12-slim` + FFmpeg only

---

## Project Structure

```
.
├── main.py           # Bot logic
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container definition
└── README.md
```

---

## Requirements

- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- A VPS with [Dokploy](https://dokploy.com) installed
- A GitHub/GitLab repo to connect to Dokploy

---

## Deploy on Dokploy

### 1. Push to a Git repo

Make sure these files are at the root of your repository:

```
main.py
requirements.txt
Dockerfile
```

### 2. Create a new application in Dokploy

- Go to your Dokploy dashboard → **Create Application**
- Connect your Git repository
- Set build type to **Dockerfile**

### 3. Set the environment variable

In Dokploy → your app → **Environment Variables**, add:

```
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Deploy

Hit **Deploy**. Dokploy will build the image and start the container.  
Your bot will be live within a minute.

---

## Local Development

### Prerequisites

- Python 3.10+
- FFmpeg installed (`apt install ffmpeg` / `brew install ffmpeg`)

### Setup

```bash
# Clone the repo
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Install dependencies
pip install -r requirements.txt

# Run the bot
BOT_TOKEN=your_token_here python main.py
```

---

## Usage

| Action | Result |
|---|---|
| `/start` or `/help` | Shows usage instructions |
| Send an MP4 video (compressed) | Bot replies with `.aac` audio |
| Send an MP4 as a file (uncompressed) | Bot replies with `.aac` audio |
| Send a non-MP4 document | Bot replies with a warning |

---

## Limitations

> **Telegram's Bot API has a 20MB file size limit** for downloads via `getFile`.  
> Videos larger than 20MB will fail to download.  
> To bypass this, you need to self-host the [Telegram Bot API server](https://github.com/tdlib/telegram-bot-api) and point the bot to it.

---

## FFmpeg Command Used

```bash
ffmpeg -y -i input.mp4 -vn -acodec aac -b:a 192k output.aac
```

| Flag | Purpose |
|---|---|
| `-y` | Overwrite output without prompting |
| `-vn` | Strip video stream |
| `-acodec aac` | Encode audio as AAC |
| `-b:a 192k` | Audio bitrate (192 kbps) |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.12 |
| Telegram SDK | pyTelegramBotAPI |
| Audio conversion | FFmpeg |
| Container | Docker (python:3.12-slim) |
| Deployment | Dokploy |

---

## License

MIT — do whatever you want with it.
