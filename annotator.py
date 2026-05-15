import cv2
import os
from pathlib import Path
from config_loader import get_config

# --- CONFIG & PATHS ---
cfg = get_config() 
IMAGE_DIR = Path(cfg['images_path'])  
LABEL_DIR = Path(cfg['labels_path']) 

if not IMAGE_DIR.exists():
    raise FileNotFoundError(f"Folder not found: {IMAGE_DIR}")

LABEL_DIR.mkdir(parents=True, exist_ok=True)

# --- SETTINGS ---
CLASSES = [
    "wc", "sink", "shower", "bath", "counter", "stove", "table", 
    "bed", "closet", "tv", "coffee_table", "fan", "co", "sd",
    "door_icon", "window_icon", "door", "window"
]    

MIN_BBOX_SIZE = 5 

drawing = False
ix, iy = -1, -1
current_img = None  
clone_img = None    
base_img = None     
bboxes = [] 
current_class_id = 0

def calculate_yolo_format(img_w, img_h, box):
    cls_id, x1, y1, x2, y2 = box
    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)
    
    x_center = ((xmin + xmax) / 2.0) / img_w
    y_center = ((ymin + ymax) / 2.0) / img_h
    width = (xmax - xmin) / img_w
    height = (ymax - ymin) / img_h
    return f"{cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"

def load_existing_annotations(txt_path, img_w, img_h):
    loaded_boxes = []
    if not txt_path.exists(): 
        return loaded_boxes
    
    with open(txt_path, 'r') as f:
        for line_idx, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            
            parts = line.split()
            if len(parts) != 5:
                print(f"\n[ERROR] Invalid format in {txt_path.name} at line {line_idx}.")
                raise ValueError(f"Format error in {txt_path.name}")

            try:
                cls_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
                
                w_pix, h_pix = width * img_w, height * img_h
                x_c_pix, y_c_pix = x_center * img_w, y_center * img_h
                xmin, ymin = int(x_c_pix - w_pix / 2), int(y_c_pix - h_pix / 2)
                xmax, ymax = int(x_c_pix + w_pix / 2), int(y_c_pix + h_pix / 2)
                
                loaded_boxes.append((cls_id, xmin, ymin, xmax, ymax))
            except ValueError:
                print(f"\n[ERROR] Corrupted data in {txt_path.name} at line {line_idx}.")
                raise ValueError(f"Numeric data error in {txt_path.name}")
                
    return loaded_boxes

def redraw_all():
    global base_img, clone_img, current_img, bboxes
    clone_img = base_img.copy()
    for box in bboxes:
        cls_id, x1, y1, x2, y2 = box
        cv2.rectangle(clone_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        class_name = CLASSES[cls_id] if cls_id < len(CLASSES) else f"ID:{cls_id}"
        cv2.putText(clone_img, class_name, (min(x1, x2), min(y1, y2) - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    current_img = clone_img.copy()

def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, current_img, clone_img, bboxes, current_class_id
    
    if event == cv2.EVENT_RBUTTONDOWN:  
        drawing = True
        ix, iy = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_img = clone_img.copy()
            cv2.rectangle(current_img, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.putText(current_img, CLASSES[current_class_id], (ix, iy - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
    elif event == cv2.EVENT_RBUTTONUP:
        drawing = False
        width = abs(x - ix)
        height = abs(y - iy)
        
        if width > MIN_BBOX_SIZE and height > MIN_BBOX_SIZE:
            bboxes.append((current_class_id, ix, iy, x, y))
            redraw_all() 
        else:
            current_img = clone_img.copy()

def main():
    global current_img, clone_img, base_img, bboxes, current_class_id
    
    images = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not images:
        print("No images found!")
        return

    cv2.namedWindow('Annotator', cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback('Annotator', draw_bbox)

    print("\n=== ANNOTATOR CONTROLS ===")
    print("RMB - Draw bbox")
    print("w,s - Change object class")
    print("d   - Save and Next image")
    print("a   - Save and Previous image")
    print("z   - Undo last bbox")
    print("c   - Clear current image annotations")
    print("q   - Quit")
    print("==================\n")

    img_idx = 0
    while img_idx < len(images):
        img_name = images[img_idx]
        img_path = IMAGE_DIR / img_name
        txt_path = LABEL_DIR / f"{img_path.stem}.txt"
        
        base_img = cv2.imread(str(img_path))
        if base_img is None:
            img_idx += 1
            continue
            
        img_h, img_w = base_img.shape[:2]
        
        try:
            bboxes = load_existing_annotations(txt_path, img_w, img_h)
        except ValueError as e:
            print(f"Skipping image due to error: {e}")
            img_idx += 1
            continue

        redraw_all()
        
        while True:
            display_img = current_img.copy()
            cv2.rectangle(display_img, (0, 0), (900, 100), (30, 30, 30), -1)
            cv2.putText(display_img, f"Class: {CLASSES[current_class_id]}", (30, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
            
            cv2.imshow('Annotator', display_img)
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('w'):
                current_class_id = (current_class_id - 1) % len(CLASSES)
            elif key == ord('s'):
                current_class_id = (current_class_id + 1) % len(CLASSES)
            elif key == ord('z'): 
                if bboxes: bboxes.pop(); redraw_all()
            elif key == ord('c'):
                bboxes = []; redraw_all()
            elif key in [ord('d'), ord('a')]:
                with open(txt_path, 'w') as f:
                    for box in bboxes:
                        f.write(calculate_yolo_format(img_w, img_h, box) + '\n')
                
                if key == ord('d'):
                    img_idx += 1
                else:
                    img_idx = max(0, img_idx - 1)
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return

if __name__ == '__main__':
    main()
