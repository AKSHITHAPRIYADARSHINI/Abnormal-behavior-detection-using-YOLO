# **Detecting Human Abnormality Using YOLO & Conv2D**

This project implements an intelligent video surveillance system capable of detecting abnormal human behavior in images, videos, and real-time camera streams using **YOLOv8** and a custom **Conv2D** model.

---

## 📁 **Project Structure**

```
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
│── UI.py                 # GUI for image prediction
│── vid.mp4               # Sample input video
│── vid_predict.py        # Video prediction script
│── yolov8n.pt            # YOLOv8 pretrained weight file
```

---

## ⭐ **Features**

* **YOLOv8-based human detection**
* **Conv2D behavior classifier** to identify:

  * Normal behavior
  * Abnormal behavior
* Supports multiple detection modes:

  * 🖼️ Image prediction
  * 🎥 Video prediction
  * 📷 Real-time webcam prediction
* **Tkinter GUI** for user-friendly interaction
* Compatible with **CPU & GPU**
* Dataset annotated using **Roboflow**
* Visualization includes:

  * Confusion matrix
  * F1-score / Precision / Recall
  * Label correlogram
  * Training accuracy & loss graphs

---

## 🛠 **Tech Stack**

* Python 3.x
* YOLOv8 (Ultralytics)
* TensorFlow / Keras (Conv2D)
* OpenCV
* Tkinter
* WandB – Model training & tracking
* Roboflow – Dataset annotation

---

## 📦 **Installation**

### 1. Create environment

```
conda create -n abnormal_env python=3.10
conda activate abnormal_env
```

### 2. Install dependencies

```
pip install ultralytics opencv-python tkinter pillow torch torchvision roboflow wandb
```

### 3. Prepare dataset

* Ensure **train/**, **test/**, **valid/** folders follow YOLO format.
* Update dataset path inside **data.yaml**.

---

## 🚀 **Running the Project**

### **Image Prediction (GUI)**

```
python UI.py
```

### **Video Prediction**

```
python vid_predict.py
```

### **Real-Time Detection**

```
python real_time.py
```

### **Training YOLO Model**

```
yolo detect train data=data.yaml model=yolov8n.pt epochs=100
```

---

## 🧠 **Model Workflow**

1. Data preprocessing
2. YOLOv8 detects human regions
3. Conv2D model analyzes cropped regions
4. Model classifies:

   * **Normal**
   * **Abnormal**
5. Bounding boxes + behavior labels drawn on output frames

---

## 📊 **Results Summary**

* High real-time FPS
* Strong mAP (50–95)
* Low false positives in confusion matrix
* High F1-score, precision, and recall
* Effectively detects:

  * Fighting
  * Aggressive gestures
  * Unmannered poses
  * Normal behavior

---

## 📌 **Screenshots (Add Your Images)**

* Image detection examples
* Video detection results
* Real-time camera output
* Training graphs & confusion matrices

---

## 📚 **Citation / Reference**

If you use this project, please cite:

**Detecting Human Abnormality Using YOLO and Conv2D**,
*Akshitha Priyadarshini M and team, 2024.*

---

## 👥 **Authors**

* **Akshitha Priyadarshini M**
* **Abitha P V**
* **Harini A K**

**RMK Engineering College**
