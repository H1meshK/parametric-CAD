# 🚀 AutoCAD Automation: Smart Part Generator

**Goal:** Generate parametric DXF parts (plates/flanges with grid holes) from simple inputs or CSV. Optional live drawing inside AutoCAD via COM (Windows only).

---

## ✅ What You Can Demo Fast
- Single DXF plate with L×W and a hole grid with margins.
- Batch-generate many DXFs from a CSV.
- Clean layer separation: `OUTER`, `HOLES`, `ANNOTATIONS`.
- Live-draw in AutoCAD using `pyautocad`.

**Units:** millimeters (DXF `$INSUNITS=4`).

---

## 📂 Project Structure
```
smart-part-generator/
├─ smart_part_generator.py
├─ requirements.txt
├─ README.md
├─ parts.csv              
├─ outputs/                   
└─ examples/                  
```

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
