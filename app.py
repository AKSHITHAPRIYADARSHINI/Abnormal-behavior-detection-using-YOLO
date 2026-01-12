from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import numpy as np
import os
from pathlib import Path
import threading
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO("yolov8n.pt")

# Global variables for video processing
processing_status = {"status": "idle", "progress": 0, "frame_count": 0, "total_frames": 0}
processing_lock = threading.Lock()
abnormal_frames = []  # Store frames with abnormal detections

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect-image', methods=['POST'])
def detect_image():
    """Detect abnormalities in a single image"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        # Read image
        image = Image.open(file.stream).convert('RGB')
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Run detection
        results = model(source=cv_image, verbose=False)
        res_plotted = results[0].plot()

        # Calculate statistics and extract detection details
        total_detections = len(results[0].boxes)
        abnormal_detections = 0
        detections_list = []

        for i, box in enumerate(results[0].boxes):
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = "Abnormal" if class_id == 1 else "Normal"

            if class_id == 1:
                abnormal_detections += 1

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections_list.append({
                "index": i,
                "class": class_name,
                "class_id": class_id,
                "confidence": round(confidence, 3),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })

        abnormality_percentage = (abnormal_detections / total_detections * 100) if total_detections > 0 else 0

        # Convert result to base64
        res_plotted_rgb = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(res_plotted_rgb)
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "image": f"data:image/png;base64,{img_str}",
            "total_detections": total_detections,
            "abnormal_detections": abnormal_detections,
            "abnormality_percentage": round(abnormality_percentage, 2),
            "detections": detections_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process a video file for abnormalities"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{timestamp}_{filename}")
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{timestamp}.avi")
        file.save(input_path)

        # Process video in background
        thread = threading.Thread(target=_process_video_background, args=(input_path, output_path))
        thread.daemon = True
        thread.start()

        return jsonify({"success": True, "message": "Video processing started", "session_id": timestamp})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _process_video_background(input_path, output_path):
    """Background thread for video processing"""
    global processing_status, abnormal_frames

    try:
        abnormal_frames = []  # Reset abnormal frames list

        with processing_lock:
            processing_status = {"status": "processing", "progress": 0, "frame_count": 0, "total_frames": 0}

        video_cap = cv2.VideoCapture(input_path)
        if not video_cap.isOpened():
            with processing_lock:
                processing_status["status"] = "error"
            return

        frame_width = int(video_cap.get(3))
        frame_height = int(video_cap.get(4))
        fps = int(video_cap.get(5))
        total_frames = int(video_cap.get(7))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        frame_count = 0
        abnormal_count = 0

        while True:
            ret, frame = video_cap.read()
            if not ret:
                break

            frame_count += 1
            results = model(source=frame, verbose=False)
            res_plotted = results[0].plot()

            total_detections = len(results[0].boxes)
            abnormal_detections = sum(1 for box in results[0].boxes if int(box.cls[0]) == 1)
            abnormal_count += abnormal_detections

            abnormality_percentage = (abnormal_detections / total_detections * 100) if total_detections > 0 else 0

            # Add text overlay
            res_plotted_copy = res_plotted.copy()
            cv2.putText(res_plotted_copy, f"Abnormality: {abnormality_percentage:.1f}%", (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(res_plotted_copy, f"Detections: {total_detections} | Abnormal: {abnormal_detections}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(res_plotted_copy, f"Frame: {frame_count}/{total_frames}", (10, 140),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)

            out.write(res_plotted_copy)

            # Store frames with abnormal detections (limit to 20 frames to avoid memory issues)
            if abnormal_detections > 0 and len(abnormal_frames) < 20:
                res_plotted_rgb = cv2.cvtColor(res_plotted_copy, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(res_plotted_rgb)
                buffer = BytesIO()
                pil_image.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()

                abnormal_frames.append({
                    "frame_number": frame_count,
                    "abnormal_count": abnormal_detections,
                    "total_detections": total_detections,
                    "abnormality_percentage": round(abnormality_percentage, 2),
                    "image": f"data:image/png;base64,{img_str}"
                })

            # Update progress
            progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
            with processing_lock:
                processing_status = {
                    "status": "processing",
                    "progress": round(progress, 2),
                    "frame_count": frame_count,
                    "total_frames": total_frames
                }

        video_cap.release()
        out.release()

        avg_abnormality = (abnormal_count / frame_count * 100) if frame_count > 0 else 0

        with processing_lock:
            processing_status = {
                "status": "completed",
                "progress": 100,
                "frame_count": frame_count,
                "total_frames": total_frames,
                "abnormal_count": abnormal_count,
                "avg_abnormality": round(avg_abnormality, 2),
                "output_file": output_path,
                "abnormal_frames": abnormal_frames
            }

        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)

    except Exception as e:
        with processing_lock:
            processing_status = {"status": "error", "error": str(e)}

@app.route('/api/video-progress', methods=['GET'])
def video_progress():
    """Get video processing progress"""
    with processing_lock:
        return jsonify(processing_status)

@app.route('/api/download-video', methods=['GET'])
def download_video():
    """Download processed video"""
    try:
        with processing_lock:
            if processing_status.get("status") != "completed" or "output_file" not in processing_status:
                return jsonify({"error": "No completed video available"}), 400

            output_file = processing_status["output_file"]

        if not os.path.exists(output_file):
            return jsonify({"error": "File not found"}), 404

        return send_file(output_file, as_attachment=True, download_name="output_video.avi")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-camera-frame', methods=['POST'])
def process_camera_frame():
    """Process a single frame from camera"""
    try:
        data = request.get_json()
        if 'frame' not in data:
            return jsonify({"error": "No frame provided"}), 400

        # Decode base64 image
        img_data = data['frame'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        image = Image.open(BytesIO(img_bytes)).convert('RGB')
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Run detection
        results = model(source=cv_image, verbose=False)
        res_plotted = results[0].plot()

        # Calculate statistics
        total_detections = len(results[0].boxes)
        abnormal_detections = 0

        # Highlight abnormal detections with red boxes
        res_plotted_copy = res_plotted.copy()
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            if class_id == 1:  # Abnormal detection
                abnormal_detections += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Draw thick red rectangle around abnormal detection
                cv2.rectangle(res_plotted_copy, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(res_plotted_copy, "ABNORMAL", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        abnormality_percentage = (abnormal_detections / total_detections * 100) if total_detections > 0 else 0

        # Add text overlay
        cv2.putText(res_plotted_copy, f"Abnormality: {abnormality_percentage:.1f}%", (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        cv2.putText(res_plotted_copy, f"Detections: {total_detections} | Abnormal: {abnormal_detections}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Convert result to base64
        res_plotted_rgb = cv2.cvtColor(res_plotted_copy, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(res_plotted_rgb)
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "frame": f"data:image/png;base64,{img_str}",
            "total_detections": total_detections,
            "abnormal_detections": abnormal_detections,
            "abnormality_percentage": round(abnormality_percentage, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-sample-video', methods=['POST'])
def process_sample_video():
    """Process the sample video file"""
    try:
        if not os.path.exists("vid.mp4"):
            return jsonify({"error": "Sample video not found"}), 404

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"output_sample_{timestamp}.avi")

        thread = threading.Thread(target=_process_video_background, args=("vid.mp4", output_path))
        thread.daemon = True
        thread.start()

        return jsonify({"success": True, "message": "Sample video processing started", "session_id": timestamp})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
