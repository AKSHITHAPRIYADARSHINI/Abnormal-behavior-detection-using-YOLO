**Detecting Human Abnormality Using YOLO & Conv2D**

This project implements an intelligent video surveillance system capable of detecting abnormal human behavior in images, videos, and real-time camera streams using YOLOv8 and a custom Conv2D model.

📁 Project Structure
abnormal_behaviour/
│── .git/                 
│── .idea/                
│── runs/                 # YOLO training outputs (weights, logs, graphs)
│── test/                 # Testing dataset
│── train/                # Training dataset
│── valid/                # Validation dataset
│── block.py              # Prediction module
│── conv.py               # Conv2D model logic
│── data.yaml             # Dataset configuration file
│── head.py               # Prediction head logic
│── output_video.avi      # Sample output video
│── real_time.py          # Real-time camera prediction
│── train.py              # Training script for YOLO/Conv2D
│── UI.py (User Interface) # GUI for image prediction
│── vid.mp4               # Sample input video
│── vid_predict.py        # Video prediction script
│── yolov8n.pt            # YOLOv8 pretrained weight file

⭐ Features

YOLOv8-based human detection

Conv2D behavior analysis to classify:

Normal behavior

Abnormal behavior

Supports multiple modes:

🖼 Image prediction

🎥 Video prediction

📷 Real-time webcam prediction

Integrated Tkinter GUI

Supports both CPU and GPU inference

Dataset trained using Roboflow annotations

Visualization of:

Confusion matrix

F1 score / Precision / Recall

Label correlogram

Training accuracy & loss

🛠 Tech Stack

Python 3.x

YOLOv8 (Ultralytics)

TensorFlow / Keras (Conv2D model)

OpenCV

Tkinter GUI

Roboflow – Annotation

WandB – Training visualization & experiment tracking

📦 Installation

Create environment

conda create -n abnormal_env python=3.10
conda activate abnormal_env


Install dependencies

pip install ultralytics opencv-python tkinter pillow torch torchvision roboflow wandb


Download dataset
Ensure your train/, test/, valid/ folders match the structure required by YOLO.

Edit dataset path in data.yaml

🚀 Running the Project
1. Image Prediction (GUI)
python UI.py

2. Video Prediction
python vid_predict.py

3. Real-Time Detection
python real_time.py

4. Training YOLO Model
yolo detect train data=data.yaml model=yolov8n.pt epochs=100

🧠 Model Workflow

Data Preprocessing

YOLOv8 detects humans

Conv2D analyzes extracted regions

Final model classifies:

Normal

Abnormal

Bounding boxes + labels drawn on output

📊 Results Summary

Real-time performance: High FPS

mAP (50–95): Consistently strong across classes

Confusion matrix: Low false positives

High F1-score, precision, and recall

Successfully identifies:

Fighting

Aggressive gestures

Unmannered poses

Normal human actions

📌 Screenshots (Overview)

✔ Image detection examples

✔ Video detection outputs

✔ Real-time camera detection

✔ Training graphs & confusion matrices

(Include your project screenshots here)

📚 Citation / Reference

If you use this project, please cite your report:

Detecting Human Abnormality Using YOLO and Conv2D,
Akshitha Priyadarshini M and team, 2024.

👥 Authors

Akshitha Priyadarshini M

Abitha P V

Harini A K

RMK Engineering College
