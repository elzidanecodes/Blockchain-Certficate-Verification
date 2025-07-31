import os
import uuid
import numpy as np
from flask import Blueprint, request, jsonify
from celery_worker import run_ocr
from celery.result import AsyncResult
from celery_worker import celery

ocr_async_bp = Blueprint("ocr_async", __name__)

@ocr_async_bp.route("/ocr_async", methods=["POST"])
def ocr_async():
    data = request.get_json()
    image_np = np.array(data.get("image_np"))
    
    filename = f"tmp_{uuid.uuid4().hex}.npy"
    path = os.path.join("tmp", filename)
    os.makedirs("tmp", exist_ok=True)
    np.save(path, image_np)

    task = run_ocr.delay(path)
    return jsonify({"task_id": task.id}), 202

@ocr_async_bp.route("/task_status/<task_id>", methods=["GET"])
def get_ocr_status(task_id):
    task = AsyncResult(task_id, app=celery)
    return jsonify({
        "state": task.state,
        "result": task.result if task.state == "SUCCESS" else None
    })
