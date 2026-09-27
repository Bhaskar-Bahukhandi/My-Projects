import cv2
from ultralytics import YOLO
import os

def dummy_vid(inp, outp):
    print("="*50)
    print(" running yolo on video ")
    print("="*50)
    
    print("loading model...")
    mdl = YOLO("yolov8n.pt")
    
    print("opening video: " + inp)
    c = cv2.VideoCapture(inp)
    if c.isOpened() == False:
        print("error cant open file")
        return
        
    w = int(c.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(c.get(cv2.CAP_PROP_FRAME_HEIGHT))
    f = int(c.get(cv2.CAP_PROP_FPS))
    tot = int(c.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print("video is %dx%d at %d fps. total frames: %d" % (w, h, f, tot))
    
    # making the writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(outp, fourcc, f, (w, h))
    
    cnt = 0
    while True == True:
        ok, frm = c.read()
        if ok == False:
            break
            
        r = mdl(frm, verbose=False)
        
        # drawing boxes
        ann = r[0].plot()
        
        out.write(ann)
        
        cnt = cnt + 1
        if cnt % 30 == 0:
            print("processed %d frames..." % cnt)
            
    c.release()
    out.release()
    print("done saving to " + outp)


def run_counter(vid_in, vid_out):
    mdl = YOLO("yolov8n.pt") 
    
    c = cv2.VideoCapture(vid_in)
    if c.isOpened() == False:
        return
        
    w = int(c.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(c.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(c.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(vid_out, fourcc, fps, (w, h))
    
    line_y = int(h / 2) + 20
    
    old_y = {}
    total_cars = 0
    
    cnt = 0
    while True == True:
        ret, frm = c.read()
        if ret == False:
            break
            
        res = mdl.track(frm, persist=True, verbose=False)
        cv2.line(frm, (0, line_y), (w, line_y), (0, 0, 255), 3)
        
        if res[0].boxes is not None and res[0].boxes.id is not None:
            boxes = res[0].boxes.xyxy.cpu().numpy()
            track_ids = res[0].boxes.id.int().cpu().tolist()
            clss = res[0].boxes.cls.cpu().tolist()
            
            idx = 0
            while idx < len(boxes):
                box = boxes[idx]
                t_id = track_ids[idx]
                c_id = clss[idx]
                
                if c_id == 2 or c_id == 7:
                    x1, y1, x2, y2 = box
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    cv2.circle(frm, (cx, cy), 5, (0, 255, 0), -1)
                    
                    if t_id in old_y:
                        prev_cy = old_y[t_id]
                        if prev_cy < line_y and cy >= line_y:
                            total_cars = total_cars + 1
                            print("car crossed! total: " + str(total_cars))
                            
                    old_y[t_id] = cy
                    
                idx = idx + 1
                
        cv2.putText(frm, "Total Vehicles: " + str(total_cars), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        out.write(frm)
        
        cnt = cnt + 1
        if cnt % 30 == 0:
            print("done %d frames..." % cnt)
            
    c.release()
    out.release()
    print("finished counting!")

if __name__ == "__main__":
    v_in = os.path.join("data", "raw_videos", "traffic.mp4")
    v_out = os.path.join("data", "processed_videos", "counted_traffic.mp4")
    if os.path.exists(v_in) == False:
        print("put traffic.mp4 in data/raw_videos!")
    else:
        run_counter(v_in, v_out)
