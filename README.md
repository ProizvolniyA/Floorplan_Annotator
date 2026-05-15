
# Floorplan_Annotator

Lightweight, custom annotation tools built with OpenCV. This repo contains two scripts for fast and efficient labeling/room segmentation of floorplans and architectural drawings supporting session resumes and multi-class selection.

## 🚀 Getting Started

**1. Clone this repository**

```bash
git clone <https://github.com/ProizvolniyA/Floorplan_Annotator>
cd <your-repository-folder>
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
sudo apt-get update
sudo apt-get install libgtk2.0-dev pkg-config python3-tk
```

**3. Configure directory paths**

Open *config.yaml* in your text editor and update the directory paths to match your local setup.
Ensure that your *images* folder contains the floorplan pages you intend to annotate.

**4. Run the launcher**

```bash
python launcher.py
```

## 🎯 The Annotation Process

Upon launching the script, a window will open displaying the first image from your folder.

*Existing Annotations:* If the image already has a corresponding .txt file in the *labels* folder, the existing bounding boxes will automatically load and be displayed on the image.

*Default State:* By default, the active object class is set to:
* "0" (which corresponds to "wc"), if you choose Object Annotator.
* "living room", if you choose Room Annotator.

*Controls:*
```text
RMB (Right Mouse Button)    -    Draw a bbox for the currently selected class(Object Annotator) / Add point of segmentation mask the currently selected class (Room Annotator).

SPACE / MMB    -    Finish current polygon (Room Annotator)

W    -    Switch to the previous object class.
S    -    Switch to the next object class.
D    -    Save the current annotations and move to the next image.
A    -    Save the current annotations and move to the previous image.
Z    -    Undo last bbox/point
C    -    Clear all annotations on the current image.
Q    -    Quit the application (without saving the current image) / Back to menu.
```

## 💡 Notes & Tips

*Resuming Work:* If you annotate only a few objects on an image, save your progress, and exit, your work is not lost. The next time you launch annotator.py, all previously drawn annotations for that image will be loaded and visible.

