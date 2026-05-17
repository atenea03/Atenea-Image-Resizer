<div align="center">

# 🖼️ Atenea Image Resizer

**Atenea-resize images to a fixed pixel size while preserving proportions and transparency.**
No internet connection required. Just open, select, and resize.

![Version](https://img.shields.io/badge/version-v2026-F5A800?style=flat-square&labelColor=1a1a1a)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square&labelColor=1a1a1a)
![License](https://img.shields.io/badge/license-Atenea_Store_Tools-F5A800?style=flat-square&labelColor=1a1a1a)

</div>

---

## 📦 Folder Contents

| File | Description |
|------|-------------|
| `ate_image_resizer.exe` | ✅ The program. Double-click to open. |
| `ate_image_resizer.py` | Source code (developers only). |
| `ate_image_resizer.spec` | PyInstaller config (developers only). |
| `logo.ico` / `logo.png` | Application icon files. |

> ⚠️ **Do not move or delete any file or folder.**
> The program needs them in their original location to run correctly.

---

## 🚀 How to Use

**Step 1 — Open the program**
- Double-click `ate_image_resizer.exe`.
- The Atenea window will open with a dark background and golden logo.

**Step 2 — Select input images**
- **📁 Select folder** → processes all matching images inside a folder.
- **🖼 Select files** → pick individual image files.
- Use **Filter by format** to limit which file types are processed.

**Step 3 — Select output folder**
- Click **Select folder** under Output folder.
- Resized files will be saved there. Default folder name: `resized`.

**Step 4 — Choose target size**
- Pick a preset size (`320×320`, `120×120`, `100×100`) from the dropdown.
- Or select **Custom** and enter your own Width and Height in pixels.

**Step 5 — Skip small images** *(optional)*
- Enable **"Skip images at or below the target resolution"** to ignore images that are already at or smaller than the target size.
- Example: target is `100×100px` — images at `50×50` or `100×100` are skipped; only images larger than `100×100` are resized.

**Step 6 — Resize**
- Click the orange **Resize** button.
- A progress bar will show the process in real time.
- When finished, a popup will show a summary: resized, skipped, errors.

---

## 🗂️ Supported Formats

| Format | Extensions | Notes |
|--------|------------|-------|
| PNG | `.png` | Lossless. Transparency preserved on canvas. |
| JPG | `.jpg` / `.jpeg` | Lossy. Transparent areas become white. |
| WEBP | `.webp` | Lossy. Transparency preserved. |
| BMP | `.bmp` | Uncompressed. Transparent areas become white. |
| TIFF | `.tiff` / `.tif` | Lossless. High quality. Large file size. |

---

## ⚙️ How Resizing Works

- Images are scaled **proportionally** (no stretching or distortion).
- The scaled image is **centered on a transparent canvas** of the exact target size. Small images are upscaled to fit.
- JPG and BMP output gets a **white background** (no transparency support).
- PNG, WEBP, and TIFF output **preserves the transparent canvas**.
- Filenames are preserved — only the dimensions change.

---

## 💡 Tips

- Use **Skip images at or below the target resolution** when processing mixed batches to avoid upscaling already-small images.
- Select **All** in the format filter to process mixed formats at once.
- The output folder is created automatically if it does not exist.
- The log box shows each file result in real time during processing.

---

<div align="center">

© 2026 **Atenea Store Tools**

</div>

Discord: https://discord.gg/mam8Nmg49d

**IMAGES:**

![1](https://i.imgur.com/nCoPnzl.png)
