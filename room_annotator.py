import cv2
import os
import json
import numpy as np
from pathlib import Path

# --- SETTINGS ---
IMAGE_DIR = Path('/floor_plans')    #please change directory
JSON_DIR = Path('/f_jsons')         #please change directory
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
    (255, 0, 0),    # living 
    (0, 255, 0),    # bedroom 
    (0, 0, 255),    # bathroom 
    (255, 255, 0),  # kitchen 
    (255, 0, 255),  # balcony 
    (0, 255, 255),  # garden 
    (200, 100, 0),  # parking 
    (0, 165, 255),  # pool 
    (128, 0, 128),  # stair 
    (100, 255, 100),# veranda 
    (150, 150, 150),# storage 
    (80, 30, 80),   # neighbor
    (0, 0, 0),      # garage    
]

JSON_DIR.mkdir(parents=True, exist_ok=True)
CLASS_KEYS = list(ROOM_LABELS.keys())

current_points = []  
annotations = {}     
current_class_idx = 0
img_idx = 0
clone_img = None
static_base = None 
needs_static_update = True 

def load_existing_json(json_path):
    if json_path.exists():
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for key in CLASS_KEYS:
                    if key not in data: data[key] = []
                return data
            except: return {key: [] for key in CLASS_KEYS}
    return {key: [] for key in CLASS_KEYS}

def update_static_base():
    
    global static_base, clone_img, annotations, needs_static_update
    
    static_base = clone_img.copy()
    overlay = clone_img.copy()
    
    for i, cls_name in enumerate(CLASS_KEYS):
        color = CLASS_COLORS[i % len(CLASS_COLORS)]
        poly_list = annotations.get(cls_name, [])
        for poly in poly_list:
            pts = np.array(poly["coordinates"][0], np.int32).reshape((-1, 1, 2))
            cv2.polylines(static_base, [pts], True, color, 3)
            cv2.fillPoly(overlay, [pts], color)
            cv2.putText(static_base, cls_name, (pts[0][0][0], pts[0][0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    

    cv2.addWeighted(overlay, 0.2, static_base, 0.8, 0, static_base)
    needs_static_update = False

def finish_polygon():
    global current_points, annotations, CLASS_KEYS, current_class_idx, needs_static_update
    if len(current_points) > 2:
        cls_name = CLASS_KEYS[current_class_idx]
        poly_data = {"type": "Polygon", "coordinates": [current_points.copy()]}
        annotations.setdefault(cls_name, []).append(poly_data)
        current_points = []
        needs_static_update = True 
        print(f"✅ ADDED: {cls_name}")

def draw_polygon_ui(event, x, y, flags, param):
    global current_points
    if event == cv2.EVENT_RBUTTONDOWN:
        current_points.append([float(x), float(y)])
    elif event == cv2.EVENT_MBUTTONDOWN:
        finish_polygon()

def main():
    global clone_img, annotations, current_points, current_class_idx, img_idx, static_base, needs_static_update
    
    images = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not images: return

    cv2.namedWindow('Room Annotator', cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback('Room Annotator', draw_polygon_ui)

    print("\n=== ROOM ANNOTATOR CONTROLS ===")
    print("RMB - Add point")
    print("SPACE / MMB - Close/Finish current polygon")
    print("w / s      - Change room class")
    print("z          - Undo last point")
    print("d          - Save and Next image")
    print("a          - Previous image")
    print("c          - Clear current image annotations")
    print("q          - Quit")
    print("===============================\n")

    while img_idx < len(images):
        img_name = images[img_idx]
        img_path = IMAGE_DIR / img_name
        json_path = JSON_DIR / f"{img_path.stem}.json"
        
        clone_img = cv2.imread(str(img_path))
        if clone_img is None:
            img_idx += 1
            continue
            
        annotations = load_existing_json(json_path)
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

            cv2.rectangle(display_img, (0, 0), (550, 60), (30, 30, 30), -1)
            cv2.putText(display_img, f"CLASS: {ROOM_LABELS[CLASS_KEYS[current_class_idx]]}", (15, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, active_color, 3)
            
            cv2.imshow('Room Annotator', display_img)
            
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('w'):
                current_class_idx = (current_class_idx - 1) % len(CLASS_KEYS)
            elif key == ord('s'):
                current_class_idx = (current_class_idx + 1) % len(CLASS_KEYS)
            elif key == ord(' '):
                finish_polygon()
            elif key == ord('z'):
                if current_points: current_points.pop()
            elif key == ord('c'):
                annotations = {key: [] for key in CLASS_KEYS}
                current_points = []
                needs_static_update = True
            elif key == ord('d'):
                with open(json_path, 'w') as f:
                    json.dump(annotations, f, indent=2)
                img_idx += 1
                break
            elif key == ord('a'):
                img_idx = max(0, img_idx - 1)
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return

if __name__ == '__main__':
    main()