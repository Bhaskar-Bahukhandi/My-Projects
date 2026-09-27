import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
import pandas as pd
import plotly.express as px
import time

# --- CONFIG ---
st.set_page_config(page_title="Traffic Dashboard", layout="wide")

def load_model():
    """
    Loads the YOLO model. We do not use @st.cache_resource here because 
    YOLO's .track() method stores internal tracking history (like BoT-SORT).
    If we cache the model, the tracker state persists between Streamlit reruns,
    causing it to lose track of all objects when a video is restarted.
    """
    return YOLO("yolov8n.pt")

# --- UI SETUP ---
st.title("🚦 Smart Traffic Analytics Dashboard")
st.markdown("Real-time vehicle detection and counting using YOLOv8.")

st.sidebar.header("Upload Video")
uploaded_file = st.sidebar.file_uploader("Choose an MP4 file", type=["mp4"])

if uploaded_file is not None:
    # Save to a temporary file for OpenCV to read
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    st.sidebar.success("Video successfully uploaded!")
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.subheader("Live Processing")
        video_placeholder = st.empty()
        
    with col2:
        st.subheader("Real-Time Analytics")
        # Live metrics
        metric_placeholder = st.empty()
        # Live chart
        chart_placeholder = st.empty()
        
    model = load_model()
    
    cap = cv2.VideoCapture(tfile.name)
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Draw the counting line slightly below the middle of the frame
        line_y = int(height / 2) + 20
        
        # State tracking
        previous_y = {}
        total_cars = 0
        
        # To make the chart dynamic, we track counts over time (simulated intervals)
        time_intervals = []
        car_counts = []
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run YOLOv8 object tracking
            results = model.track(frame, persist=True, verbose=False)
            
            # Draw the counting boundary line
            cv2.line(frame, (0, line_y), (width, line_y), (0, 0, 255), 3)
            
            # Process detections
            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                classes = results[0].boxes.cls.cpu().tolist()
                
                for box, track_id, cls_id in zip(boxes, track_ids, classes):
                    # Class 2 = car, 5 = bus, 7 = truck in COCO dataset
                    if cls_id in [2, 5, 7]:
                        x1, y1, x2, y2 = box
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        
                        # Draw tracking dot
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                        
                        # Check if vehicle crossed the line (moving downwards)
                        if track_id in previous_y:
                            prev_cy = previous_y[track_id]
                            if prev_cy < line_y and cy >= line_y:
                                total_cars += 1
                                
                        previous_y[track_id] = cy
                    
            # Annotate total count on the frame
            cv2.putText(frame, f"Total Vehicles: {total_cars}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            
            # --- UI UPDATES ---
            frame_count += 1
            
            # To prevent Streamlit's websocket from crashing on 4K videos, 
            # we resize the display frame and only send every 3rd frame to the browser.
            if frame_count % 3 == 0:
                display_frame = cv2.resize(frame, (800, int(800 * (height / width))))
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB")
                
            # Update the dashboard analytics every 15 frames
            if frame_count % 15 == 0:
                metric_placeholder.metric(label="Total Vehicles Counted", value=total_cars)
                
                # Append to our live data lists
                current_elapsed = int(time.time() - start_time)
                time_intervals.append(current_elapsed)
                car_counts.append(total_cars)
                
                # Render live chart
                df = pd.DataFrame({"Seconds Elapsed": time_intervals, "Cumulative Count": car_counts})
                fig = px.area(df, x="Seconds Elapsed", y="Cumulative Count", title="Live Traffic Volume")
                chart_placeholder.plotly_chart(fig, width="stretch")

            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")
                
        cap.release()
        st.success("✅ Video processing complete!")
else:
    st.info("👈 Please upload a traffic video on the left sidebar to start.")
