# 🚀 Python + AutoCAD Automation: Smart Part Generator

**Goal:** Generate parametric DXF parts (plates/flanges with grid holes) from simple inputs or CSV. Optional live drawing inside AutoCAD via COM (Windows only).

---

## ✅ What You Can Demo Fast
- Single DXF plate with L×W and a hole grid with margins.
- Batch-generate many DXFs from a CSV.
- Clean layer separation: `OUTER`, `HOLES`, `ANNOTATIONS`.
- (Optional) Live-draw in AutoCAD using `pyautocad`.

**Units:** millimeters (DXF `$INSUNITS=4`).

---

## 📂 Project Structure
```
smart-part-generator/
├─ smart_part_generator.py
├─ requirements.txt
├─ README.md
├─ parts.csv                  # sample batch file
├─ outputs/                   # your DXFs will appear here
└─ examples/                  # (optional) screenshots later
```

---

## 🪜 Stages (follow in order)

### Stage 1 — Setup & Sanity Check (10–15 min)
1. Create and activate a virtual environment (Windows PowerShell):
   ```ps1
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run a dry test (no AutoCAD needed):
   ```bash
   python smart_part_generator.py --length 120 --width 80 --margin 10 --hole_diameter 6 --rows 3 --cols 4
   ```
3. Open the DXF from `outputs/` in any CAD app/viewer. You should see:
   - Outer rectangle (plate)
   - Grid of circles (holes)
   - Corner note text with parameters

### Stage 2 — CSV Batch Generation (15 min)
1. Edit `parts.csv` (already provided) or make your own.
2. Run:
   ```bash
   python smart_part_generator.py --csv parts.csv
   ```
3. Multiple DXFs will land in `outputs/`. File names encode parameters for quick traceability.

### Stage 3 — Smart Spacing & Validation (10 min)
- The script already computes hole spacing to fit within margins.
- Edge cases handled: single row/col, tiny margins, oversized holes, negative values.
- If anything is invalid, you'll get clear error messages.

### Stage 4 (Optional, Windows + AutoCAD) — Live AutoCAD Drawing (20–30 min)
1. Ensure AutoCAD is installed and open.
2. Run with the flag:
   ```bash
   python smart_part_generator.py --length 120 --width 80 --margin 10 --hole_diameter 6 --rows 3 --cols 4 --draw_live
   ```
3. The tool will use COM to send lines/circles into the active AutoCAD document.
   - If `pyautocad`/`pywin32` are missing or not on Windows, it will **fallback** automatically and still write DXF.

### Stage 5 — Polish for Resume/GitHub (15–30 min)
- Add 1–2 screenshots of the DXF opened in AutoCAD/Blender to `examples/`.
- Create a short demo GIF if you can (optional).
- Push to GitHub:
  ```bash
  git init
  git add .
  git commit -m "Smart Part Generator: DXF automation with Python"
  git branch -M main
  git remote add origin <your_repo_url>
  git push -u origin main
  ```

---

## 🧪 Quick Examples

- Single part:
  ```bash
  python smart_part_generator.py --length 200 --width 100 --margin 12 --hole_diameter 8 --rows 4 --cols 7
  ```

- Batch from CSV:
  ```bash
  python smart_part_generator.py --csv parts.csv
  ```

- Live draw (Windows + AutoCAD):
  ```bash
  python smart_part_generator.py --length 150 --width 90 --margin 8 --hole_diameter 5 --rows 3 --cols 5 --draw_live
  ```

---

## 🗂 CSV Schema

Required columns (header names must match, case-insensitive ok):
```
name,length,width,margin,hole_diameter,rows,cols,material,thickness
```

- **name**: becomes part of filename (no spaces recommended)
- **length,width,margin,hole_diameter,thickness**: numbers in **mm**
- **rows,cols**: integers (0=skip holes)
- **material**: free text for note only

If a row is invalid (e.g., holes don't fit), that row is skipped with a clear error printed.

---

## ❗ Common Pitfalls & Fixes
- **"Holes overlap or don't fit"** → Increase plate size, reduce `rows/cols`, reduce `hole_diameter`, or increase `length/width`/decrease `margin`.
- **"pyautocad not found"** → You're not on Windows or AutoCAD isn't installed. Omit `--draw_live`. DXF generation still works 100%.
- **DXF looks unitless** → We set `$INSUNITS=4 (mm)`. Most viewers read it correctly.
- **Text too small/large** → Change `--text_height` flag.

---

## 📝 Resume Line (you can use this verbatim)
> Built a Python-based CAD automation tool that programmatically generates parametric engineering parts (DXF) with customizable features. Automated repetitive drafting tasks, integrated annotations, and demonstrated Industry 4.0 by linking design parameters to programmatic generation. Optional AutoCAD COM version enabled live CAD drawing.

---

## 🧠 How It Works (in 20 seconds)
- Make a new DXF document, set units to mm, add 3 layers.
- Draw a rectangle for the plate.
- Compute grid bounds = plate minus margins.
- Evenly distribute `rows × cols` hole centers inside the grid.
- Save to `outputs/<auto_name>.dxf`. Optionally mirror it live into AutoCAD.

You're done. Simple, clean, hire-worthy.