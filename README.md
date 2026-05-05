# Floorplan_Annotator

A lightweight, custom bounding-box annotation tool built with OpenCV. This script is designed for fast and efficient labeling of floorplans and architectural drawings, supporting session resumes and multi-class selection.

## 🚀 Getting Started

**1. Clone this repository**

```bash
git clone <https://github.com/ProizvolniyA/Floorplan_Annotator>
cd <your-repository-folder>
```

**2. Install dependencies**

```bash
pip install opencv-python
```
**3. Configure directory paths**

Open *annotator.py* in your text editor and update the directory paths to match your local setup.
Ensure that your *images* folder contains the floorplan pages you intend to annotate.

**4. Run the annotator**

```bash
python annotator.py
```

## 🎯 The Annotation Process

Upon launching the script, a window will open displaying the first image from your folder.

*Existing Annotations:* If the image already has a corresponding .txt file in the *labels* folder, the existing bounding boxes will automatically load and be displayed on the image.

*Default State:* By default, the active object class is set to "0" (which corresponds to "wc").

Hold RMB (Right Mouse Button),Draw a bounding box for the currently selected class.

```text
W - Switch to the previous object class.
S - Switch to the next object class.
D - Save the current annotations and move to the next image.
A - Move to the previous image.
C - Clear all annotations on the current image.
Q - Quit the application (without saving the current image).
```

## 💡 Notes & Tips

*Resuming Work:* If you annotate only a few objects on an image, save your progress, and exit, your work is not lost. The next time you launch annotator.py, all previously drawn bounding boxes for that image will be loaded and visible.

*Manual Editing:* If you need to manually tweak coordinates or remove a specific bounding box, you can directly edit the corresponding .txt file located in the *labels* directory.





