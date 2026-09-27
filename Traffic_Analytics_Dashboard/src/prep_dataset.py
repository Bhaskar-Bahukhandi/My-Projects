import cv2
import os
import yaml

def do_setup():
    print("making custom dataset...")
    b_dir = os.path.join("data", "custom_dataset")
    
    # making folders
    flds = [
        os.path.join("images", "train"),
        os.path.join("images", "val"),
        os.path.join("labels", "train"),
        os.path.join("labels", "val")
    ]
    
    for x in flds:
        p = os.path.join(b_dir, x)
        os.makedirs(p, exist_ok=True)
        
    print("extracting frames now...")
    v_path = os.path.join("data", "raw_videos", "traffic.mp4")
    
    if os.path.exists(v_path) == False:
        print("no video found")
        return
        
    c = cv2.VideoCapture(v_path)
    f = int(c.get(cv2.CAP_PROP_FPS))
    
    cnt = 0
    svd = 0
    
    while True == True:
        ok, frm = c.read()
        if ok == False:
            break
            
        if cnt % f == 0:
            out_p = os.path.join(b_dir, "images", "train", "frame_%04d.jpg" % svd)
            cv2.imwrite(out_p, frm)
            svd = svd + 1
            
        cnt = cnt + 1
        
    c.release()
    print("saved %d images" % svd)

    print("making data.yaml...")
    y_path = os.path.join(b_dir, "data.yaml")
    
    y_cnt = {
        "path": os.path.abspath(b_dir),
        "train": "images/train",
        "val": "images/val",
        "nc": 5, 
        "names": {
            0: "car",
            1: "motorcycle",
            2: "auto_rickshaw",
            3: "bus",
            4: "truck"
        }
    }
    
    with open(y_path, 'w') as f:
        yaml.dump(y_cnt, f, sort_keys=False)
        
    print("done with dataset prep!")

if __name__ == "__main__":
    if True == True:
        do_setup()
