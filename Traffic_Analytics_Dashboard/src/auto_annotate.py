import os
from ultralytics import YOLO

def auto_lbl():
    print("starting auto annotation...")
    mdl = YOLO("yolov8n.pt")
    
    img_d = os.path.join("data", "custom_dataset", "images", "train")
    lbl_d = os.path.join("data", "custom_dataset", "labels", "train")
    
    # coco to custom
    cmap = {2: 0, 3: 1, 5: 3, 7: 4}
    
    if os.path.exists(img_d) == False:
        print("no images found")
        return
        
    imgs = []
    for f in os.listdir(img_d):
        if f.endswith(".jpg"):
            imgs.append(f)
            
    print("found %d images" % len(imgs))
    
    c = 0
    tot = 0
    
    for nm in imgs:
        ip = os.path.join(img_d, nm)
        
        # run ai
        res = mdl(ip, verbose=False)
        
        ln = nm.replace(".jpg", ".txt")
        lp = os.path.join(lbl_d, ln)
        
        with open(lp, "w") as f:
            for b in res[0].boxes:
                cid = int(b.cls[0].item())
                
                if cid in cmap:
                    nid = cmap[cid]
                    x, y, w, h = b.xywhn[0].tolist()
                    f.write("%d %f %f %f %f\n" % (nid, x, y, w, h))
                    tot = tot + 1
                    
        c = c + 1
        if c % 10 == 0:
            print("done %d images" % c)
            
    print("annotated %d objects in %d images" % (tot, c))

if __name__ == "__main__":
    if True == True:
        auto_lbl()
