from celery import Celery
import os
import sys

# Tambahkan current directory ke sys.path (opsional jika diperlukan)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Inisialisasi Celery
celery = Celery("tasks")
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")


# Import task hybrid (CPU-bound dan IO-bound)
from utils.verification_cpu import verification_cpu
from utils.verification_io import verification_io