import cv2
import os
import json
import numpy as np
from pathlib import Path
from config_loader import get_config

# --- CONFIG & PATHS ---
try:
    cfg = get_config() 
    IMAGE_DIR = Path(cfg['images_path']) 
    JSON_DIR = Path(cfg['geom_path'])   

    if not IMAGE_DIR.exists():
        print(f"[ERROR] Image directory not found: {IMAGE_DIR}")
        input("Press Enter to exit...")
        exit(1)

    JSON_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"[ERROR] Config loading failed: {e}")
    input("Press Enter to exit...")
    exit(1)
     
# --- SETTINGS ---
ROOM_LABELS = {
    "living": "LIVING ROOM",
    "bedroom": "BEDROOM",
    "bathroom": "BATH",
    "kitchen": "KITCHEN",
    "balcony": "BALCONY",
    "garden": "GARDEN",
    "parking": "PARKING",
    "pool": "POOL",
    "stair": "STAIR",
    "veranda": "VERANDA",
    "storage": "STORAGE",
    "neighbor": "NEIGHBOR",
    "garage": "GARAGE",
}

CLASS_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (200, 100, 0), (0, 165, 255),
    (128, 0, 128), (100, 255, 100), (150, 150, 150), (80, 30, 80), (0, 0, 0)
]

CLASS_KEYS = list(ROOM_LABELS.keys())

current_points = []  
annotations = {}     
current_class_idx = 0
img_idx = 0
clone_img = None
static_base = None 
needs_static_update = True 

def load_existing_json(json_path):
    template = {key: [] for key in CLASS_KEYS}
    if not json_path.exists():
        return template
    
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("JSON root must be a dictionary")
            
            for cls_name in CLASS_KEYS:
                if cls_name not in data:
                    data[cls_name] = []
                elif not isinstance(data[cls_name], list):
                    data[cls_name] = []
            
            return data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"\n[CRITICAL] JSON Corrupted: {json_path.name}. Error: {e}")
            raise 

def update_static_base():
    global static_base, clone_img, annotations, needs_static_update
    if clone_img is None: return
    
    static_base = clone_img.copy()
    overlay = clone_img.copy()
    
    for i, cls_name in enumerate(CLASS_KEYS):
        color = CLASS_COLORS[i % len(CLASS_COLORS)]
        poly_list = annotations.get(cls_name, [])
        for poly in poly_list:
            if "coordinates" in poly and poly["coordinates"]:
                pts = np.array(poly["coordinates"][0], np.int32).reshape((-1, 1, 2))
                cv2.polylines(static_base, [pts], True, color, 3)
                cv2.fillPoly(overlay, [pts], color)
                cv2.putText(static_base, cls_name, (pts[0][0][0], pts[0][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    cv2.addWeighted(overlay, 0.2, static_base, 0.8, 0, static_base)
    needs_static_update = False

def finish_polygon():
    global current_points, annotations, current_class_idx, needs_static_update
    if len(current_points) > 2:
        cls_name = CLASS_KEYS[current_class_idx]
        poly_data = {"type": "Polygon", "coordinates": [current_points.copy()]}
        annotations.setdefault(cls_name, []).append(poly_data)
        current_points = []
        needs_static_update = True 
        print(f"✅ Added room: {cls_name}")

def draw_polygon_ui(event, x, y, flags, param):
    global current_points
    if event == cv2.EVENT_RBUTTONDOWN:
        current_points.append([float(x), float(y)])
    elif event == cv2.EVENT_MBUTTONDOWN:
        finish_polygon()

def main():
    global clone_img, annotations, current_points, current_class_idx, img_idx, static_base, needs_static_update
    
    images = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not images:
        print("No images found in directory!")
        return

    cv2.namedWindow('Room Annotator', cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback('Room Annotator', draw_polygon_ui)

    print("\n=== ROOM ANNOTATOR CONTROLS ===")
    
    print("RMB         - Add point")
    print("SPACE / MMB - Close/Finish current polygon")
    print("w / s       - Change room class")
    print("z           - Undo last point")
    print("d           - Save and Next image")
    print("a           - Save and Previous image")
    print("c           - Clear current image annotations")
    print("q           - Quit")
    print("===============================\n")

    while img_idx < len(images):
        img_name = images[img_idx]
        img_path = IMAGE_DIR / img_name
        json_path = JSON_DIR / f"{img_path.stem}.json"
        
        clone_img = cv2.imread(str(img_path))
        if clone_img is None:
            img_idx += 1
            continue
            
        try:
            annotations = load_existing_json(json_path)
        except Exception:
            print(f"!!! Error in {json_path.name}. Skipping file to prevent data loss.")
            img_idx += 1
            continue

        current_points = []
        needs_static_update = True 

        while True:
            if needs_static_update:
                update_static_base()

            display_img = static_base.copy() 
            active_color = CLASS_COLORS[current_class_idx % len(CLASS_COLORS)]

            if len(current_points) > 0:
                pts_tmp = np.array(current_points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(display_img, [pts_tmp], False, active_color, 2)
                for p in current_points:
                    cv2.circle(display_img, (int(p[0]), int(p[1])), 5, active_color, -1)

            rect_width, rect_height = 1200, 150
            cv2.rectangle(display_img, (0, 0), (rect_width, rect_height), (30, 30, 30), -1)
            cv2.rectangle(display_img, (0, 0), (rect_width, rect_height), (200, 200, 200), 2)
            
            text = f"CLASS: {ROOM_LABELS[CLASS_KEYS[current_class_idx]]}"
            cv2.putText(display_img, text, (30, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, active_color, 7)
    
            cv2.imshow('Room Annotator', display_img)
            
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('w'):
                current_class_idx = (current_class_idx - 1) % len(CLASS_KEYS)
            elif key == ord('s'):
                current_class_idx = (current_class_idx + 1) % len(CLASS_KEYS)
            elif key == ord(' '): 
                finish_polygon()
            elif key == ord('z'):
                if current_points: 
                    current_points.pop()
                else: 
                    cls_name = CLASS_KEYS[current_class_idx]
                    if annotations[cls_name]:
                        annotations[cls_name].pop()
                        needs_static_update = True
            elif key == ord('c'):
                annotations = {key: [] for key in CLASS_KEYS}
                current_points = []
                needs_static_update = True
            elif key in [ord('d'), ord('a')]:
                with open(json_path, 'w') as f:
                    json.dump(annotations, f, indent=2)
                print(f"Saved: {json_path.name}")
                
                if key == ord('d'): img_idx += 1
                else: img_idx = max(0, img_idx - 1)
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return

if __name__ == '__main__':
    main()
