import cv2
from ultralytics import YOLO
import os

def run_vid(inp, outp):
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
    
    # now actually do the training part down here
    print("ok now actually doing the training part...")
    y_p = os.path.abspath(os.path.join("data", "custom_dataset", "data.yaml"))
    if os.path.exists(y_p) == True:
        print("training now...")
        # just 5 epochs for testing
        mdl.train(data=y_p, epochs=5, imgsz=320, batch=4, project="models", name="custom_traffic")
        print("done!")

if __name__ == "__main__":
    v_in = os.path.join("data", "raw_videos", "traffic.mp4")
    v_out = os.path.join("data", "processed_videos", "dummy_output.mp4")
    
    if os.path.exists(v_in) == False:
        print("put traffic.mp4 in data/raw_videos!")
    else:
        run_vid(v_in, v_out)
