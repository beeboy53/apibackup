import yt_dlp
import logging
import tempfile
import os

class YtdlpLogger:
    def debug(self, msg):
        pass
    def info(self, msg):
        logging.info(msg)
    def warning(self, msg):
        logging.warning(msg)
    def error(self, msg):
        logging.error(msg)

def download_video(url: str, download_options: dict) -> dict:
    base_opts = {
        'logger': YtdlpLogger(),
        'outtmpl': '/downloads/%(id)s.%(ext)s',
        'noplaylist': True,
    }
    ydl_opts = {**base_opts, **download_options}
    cookie_string = ydl_opts.pop('cookie_string', None)
    temp_cookie_file = None
    try:
        if cookie_string:
            temp_cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8')
            temp_cookie_file.write(cookie_string)
            temp_cookie_file.close()
            ydl_opts['cookiefile'] = temp_cookie_file.name

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info(f"Starting download for URL: {url}")
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            logging.info(f"Successfully downloaded: {filename}")
            
            # We no longer need the full file path, just the info for the frontend
            return {
                'status': 'SUCCESS',
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                # We will construct the final download URL in the FastAPI app
                'filename': os.path.basename(filename) 
            }
    except Exception as e:
        logging.error(f"An unexpected error occurred for {url}: {e}")
        return {'status': 'ERROR', 'message': str(e)}
    finally:
        if temp_cookie_file:
            os.unlink(temp_cookie_file.name)