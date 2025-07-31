from celery import chain
from utils.ocr_utils import run_ocr_and_extract
from utils.hash_utils import run_hashing
from utils.rsa_utils import run_signature_check
from utils.ipfs_utils import run_regenerate_ipfs
from utils.log_utils import run_logging

task = chain(
    run_ocr_and_extract.s(file_path),
    run_hashing.s(),
    run_signature_check.s(),
    run_regenerate_ipfs.s(),
    run_logging.s()
)
task.delay()