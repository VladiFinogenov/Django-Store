# This will make sure the src is always imported when
# Django starts so that shared_task will use this src.

# Это гарантирует, что ваш src будет загружен, когда Django запускается.
from .celery import app as celery_app

__all__ = ('celery_app',)
