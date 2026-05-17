import os
import subprocess
import tempfile
import logging
import telebot
from telebot.types import Message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def download_telegram_file(file_id: str, suffix: str) -> str:
    """Download a Telegram file to a temp path and return the path."""
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(downloaded)
    tmp.close()
    logger.info(f"Downloaded file to {tmp.name}")
    return tmp.name


def convert_to_aac(input_path: str) -> str:
    """Run ffmpeg to extract audio as AAC. Returns output path."""
    output_path = input_path.rsplit(".", 1)[0] + ".aac"
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",                  # no video
        "-acodec", "aac",
        "-b:a", "192k",
        output_path
    ]
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"ffmpeg stderr: {result.stderr}")
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    logger.info(f"Converted to {output_path}")
    return output_path


def handle_video_file(message: Message, file_id: str, file_name: str = "audio"):
    """Core handler: download → convert → reply → cleanup."""
    input_path = None
    output_path = None
    try:
        bot.reply_to(message, "⏳ Converting your video to AAC, please wait...")

        input_path = download_telegram_file(file_id, ".mp4")
        output_path = convert_to_aac(input_path)

        base_name = os.path.splitext(file_name)[0] + ".aac"

        with open(output_path, "rb") as audio_file:
            bot.send_audio(
                message.chat.id,
                audio_file,
                caption="✅ Here is your AAC audio!",
                title=base_name,
                reply_to_message_id=message.message_id
            )
        logger.info(f"Sent AAC to chat {message.chat.id}")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        bot.reply_to(message, f"❌ Failed to convert: {e}")
    finally:
        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"Cleaned up {path}")


@bot.message_handler(commands=["start", "help"])
def handle_start(message: Message):
    bot.reply_to(
        message,
        "🎬 Send me any MP4 video and I'll extract the audio as an AAC file.\n\n"
        "Just drop your video here!"
    )


@bot.message_handler(content_types=["video"])
def handle_video(message: Message):
    """Handles videos sent natively (compressed by Telegram)."""
    video = message.video
    file_name = getattr(video, "file_name", None) or "video.mp4"
    logger.info(f"Received video: {file_name} ({video.file_size} bytes)")
    handle_video_file(message, video.file_id, file_name)


@bot.message_handler(content_types=["document"])
def handle_document(message: Message):
    """Handles videos sent as files (uncompressed)."""
    doc = message.document
    mime = doc.mime_type or ""
    file_name = doc.file_name or "file"

    if mime != "video/mp4" and not file_name.lower().endswith(".mp4"):
        bot.reply_to(message, "⚠️ Please send an MP4 file.")
        return

    logger.info(f"Received document: {file_name} ({doc.file_size} bytes)")
    handle_video_file(message, doc.file_id, file_name)


if __name__ == "__main__":
    logger.info("Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
