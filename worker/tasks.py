from .celery_app import celery_app
from core.downloader import download_video

@celery_app.task(bind=True)
def download_video_task(self, url: str, download_options: dict):
    result = download_video(url, download_options)
    return result