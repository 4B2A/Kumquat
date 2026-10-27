# 🍊 Kumquat — Cozy Desktop Blur Tool

Kumquat is a minimalist, lightweight, and **privacy-first** desktop application designed to blur, pixelate, or censor parts of your images instantly. Built with a beautiful open pastel purple and blue aesthetic, it provides a cozy and fluid user experience.

No cloud uploads, no heavy photo-editing software load times. Just drag, select, and save locally.

## 🚀 How to Download and Run (Windows)

You don't need to install Python or any code dependencies to use Kumquat. Just follow these simple steps:

1. Go to the **[Releases](https://github.com)** section on the right side of this GitHub page.
2. Download the latest **`Kumquat.exe`** file from the assets list.
3. Move the downloaded `.exe` file to your **Desktop** (or any folder you prefer).
4. **Double-click** `Kumquat.exe` to launch the application instantly!

---

## ✨ Features
* **Privacy First:** 100% offline processing. Your photos never leave your computer.
* **Cozy UI:** Apple-inspired borderless frame design featuring soothing pastel purple and blue tones.
* **Censorship Modes:** 
  * 💧 **Soft Blur:** Smooth and beautiful Gaussian blur.
  * 🧱 **Pixelate/Mosaic:** Classic retro pixel block censoring.
  * ⬛ **Solid Tape:** Clean, matte dark privacy bars.
* **Ultra-Fast Workflow:** Simply press **`S`** on your keyboard to instantly save the censored output in the same directory without overwriting the original file (automatically handles indexing like `_1`, `_2`).

## 🛠️ Developer Setup (Run from Source)

If you prefer to run or build the application from the source code, make sure you have Python 3.12 installed:

```bash
# Clone the repository
git clone https://github.com/4B2A/Kumquat
cd Kumqua

# Install dependencies
pip install PyQt6 Pillow

# Run the app
python app.py
```

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
