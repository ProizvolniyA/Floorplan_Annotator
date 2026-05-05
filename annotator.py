import cv2
import os
from pathlib import Path

# --- SETTINGS ---
IMAGE_DIR = Path('/floorplans')    #please, change directory  
LABEL_DIR = Path('/f_labels')      #please, change directory
CLASSES = [
    "wc", "sink", "shower", "bath", "counter", "stove", "table", 
    "bed", "closet", "tv", "coffee_table", "fan", "co", "sd",
    "door_icon", "window_icon", "door", "window"
]    

LABEL_DIR.mkdir(parents=True, exist_ok=True)

drawing = False
ix, iy = -1, -1
current_img = None
clone_img = None
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
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                cls_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
                
                w_pix = width * img_w
                h_pix = height * img_h
                x_center_pix = x_center * img_w
                y_center_pix = y_center * img_h
                
                xmin = int(x_center_pix - w_pix / 2)
                ymin = int(y_center_pix - h_pix / 2)
                xmax = int(x_center_pix + w_pix / 2)
                ymax = int(y_center_pix + h_pix / 2)
                
                loaded_boxes.append((cls_id, xmin, ymin, xmax, ymax))
    return loaded_boxes

def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, current_img, clone_img, bboxes, current_class_id
    
    if event == cv2.EVENT_RBUTTONDOWN:  
        drawing = True
        ix, iy = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            current_img = clone_img.copy()
            cv2.rectangle(current_img, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.putText(current_img, CLASSES[current_class_id], (ix, iy - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
    elif event == cv2.EVENT_RBUTTONUP:
        drawing = False
        cv2.rectangle(clone_img, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.putText(clone_img, CLASSES[current_class_id], (ix, iy - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        current_img = clone_img.copy()
        bboxes.append((current_class_id, ix, iy, x, y))
    
def main():
    global current_img, clone_img, bboxes, current_class_id
    
    images = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not images:
        print("There is no images here :(")
        return

    cv2.namedWindow('Annotator', cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback('Annotator', draw_bbox)

    print("=== УПРАВЛЕНИЕ ===")
    print("ПКМ - Рисовать рамку")
    print("w,s - Выбор активного класса")
    print("d   - Следующая картинка (сохранение)")
    print("a   - Предыдущая картинка")
    print("c   - Очистить разметку на текущей картинке")
    print("q   - Выйти")
    print("==================\n")

    img_idx = 0
    while img_idx < len(images):
        img_name = images[img_idx]
        img_path = IMAGE_DIR / img_name
        txt_path = LABEL_DIR / f"{img_path.stem}.txt"
        
        current_img = cv2.imread(str(img_path))
        if current_img is None:
            img_idx += 1
            continue
            
        img_h, img_w = current_img.shape[:2]
        
        # --- OLD BBOXES ---
        bboxes = load_existing_annotations(txt_path, img_w, img_h)
        clone_img = current_img.copy()
        
        for box in bboxes:
            cls_id, x1, y1, x2, y2 = box
            cv2.rectangle(clone_img, (x1, y1), (x2, y2), (255, 0, 0), 2) 
            
            class_name = CLASSES[cls_id] if cls_id < len(CLASSES) else f"ID:{cls_id}"
            
            cv2.putText(clone_img, class_name, (min(x1,x2), min(y1,y2) - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
        current_img = clone_img.copy()
        
        print(f"Opened file: {img_name} | Current class: {CLASSES[current_class_id]}")

        while True:
            display_img = current_img.copy()
            cv2.putText(display_img, f"Class: {CLASSES[current_class_id]}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            cv2.imshow('Annotator', display_img)
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('w'):
                current_class_id = (current_class_id - 1) % len(CLASSES)
            elif key == ord('s'):
                current_class_id = (current_class_id + 1) % len(CLASSES)
            
            elif key == ord('c'):
                current_img = cv2.imread(str(img_path))
                clone_img = current_img.copy()
                bboxes = []
                print("Annotation destroyed.")
                
            elif key == ord('d'):
                with open(txt_path, 'w') as f:
                    for box in bboxes:
                        yolo_str = calculate_yolo_format(img_w, img_h, box)
                        f.write(yolo_str + '\n')
                print(f"✅ Saved: {txt_path.name}")
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