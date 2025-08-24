#!/usr/bin/env python3
"""
Smart Part Generator — DXF + (optional) live AutoCAD drawing

Usage examples:
    python smart_part_generator.py --length 120 --width 80 --margin 10 --hole_diameter 6 --rows 3 --cols 4
    python smart_part_generator.py --csv parts.csv
    python smart_part_generator.py --length 150 --width 90 --margin 8 --hole_diameter 5 --rows 3 --cols 5 --draw_live
"""
from __future__ import annotations
import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

# --- Optional AutoCAD imports guarded ---
def _try_import_autocad():
    try:
        from pyautocad import Autocad, APoint  # type: ignore
        return Autocad, APoint
    except Exception:
        return None, None

# --- DXF imports ---
try:
    import ezdxf
    from ezdxf import units
except Exception as e:
    print("ERROR: ezdxf is required. Install with: pip install ezdxf", file=sys.stderr)
    raise

OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)

@dataclass
class PartSpec:
    name: str = "plate"
    length: float = 100.0   # mm
    width: float = 60.0     # mm
    margin: float = 10.0    # mm (uniform on all sides)
    hole_diameter: float = 6.0  # mm
    rows: int = 0           # 0 => no holes
    cols: int = 0
    material: str = ""
    thickness: float = 0.0  # mm
    text_height: float = 3.0  # mm for annotations
    draw_live: bool = False

    def validate(self) -> None:
        if self.length <= 0 or self.width <= 0:
            raise ValueError("length and width must be > 0")
        if self.margin < 0:
            raise ValueError("margin must be >= 0")
        if self.hole_diameter < 0:
            raise ValueError("hole_diameter must be >= 0")
        if self.rows < 0 or self.cols < 0:
            raise ValueError("rows and cols cannot be negative")
        # Check grid space if holes present
        if self.rows > 0 and self.cols > 0 and self.hole_diameter > 0:
            grid_w = self.length - 2 * self.margin
            grid_h = self.width - 2 * self.margin
            if grid_w <= 0 or grid_h <= 0:
                raise ValueError("margins too large: no space left for holes")
            # Quick feasibility: minimal spacing so circles don't overlap
            # We allow touching at the extreme edges but not overlapping.
            import math
            min_dx = 0 if self.cols == 1 else grid_w / (self.cols - 1)
            min_dy = 0 if self.rows == 1 else grid_h / (self.rows - 1)
            if self.cols == 1 and self.rows == 1:
                # Single hole must fit inside grid with diameter clearance
                if self.hole_diameter > min(grid_w, grid_h):
                    raise ValueError("single hole diameter larger than available grid area")
            else:
                if min_dx < self.hole_diameter or min_dy < self.hole_diameter:
                    raise ValueError("holes too dense: increase plate/margins or reduce rows/cols/diameter")

def build_filename(spec: PartSpec) -> str:
    base = f"{spec.name}_{int(spec.length)}x{int(spec.width)}"
    if spec.rows and spec.cols and spec.hole_diameter:
        base += f"_r{spec.rows}c{spec.cols}_d{int(spec.hole_diameter)}_m{int(spec.margin)}"
    if spec.thickness:
        base += f"_t{int(spec.thickness)}"
    if spec.material:
        base += f"_{spec.material}"
    return base.replace(" ", "_") + ".dxf"

def create_new_doc() -> "ezdxf.EzdxfDocument":
    doc = ezdxf.new(setup=True)
    doc.header["$INSUNITS"] = 4  # millimeters # sets $INSUNITS=4 internally
    # Create layers
    doc.layers.new(name="OUTER", dxfattribs={"color": 7})        # white/black
    doc.layers.new(name="HOLES", dxfattribs={"color": 1})        # red-ish
    doc.layers.new(name="ANNOTATIONS", dxfattribs={"color": 3})  # green-ish
    return doc

def draw_plate(msp, length: float, width: float):
    # Rectangle from (0,0) to (length,width)
    msp.add_line((0,0), (length,0), dxfattribs={"layer": "OUTER"})
    msp.add_line((length,0), (length,width), dxfattribs={"layer": "OUTER"})
    msp.add_line((length,width), (0,width), dxfattribs={"layer": "OUTER"})
    msp.add_line((0,width), (0,0), dxfattribs={"layer": "OUTER"})

def hole_centers(spec: PartSpec) -> List[Tuple[float,float]]:
    if spec.rows <= 0 or spec.cols <= 0 or spec.hole_diameter <= 0:
        return []
    grid_w = spec.length - 2 * spec.margin
    grid_h = spec.width - 2 * spec.margin
    xs = []
    ys = []
    if spec.cols == 1:
        xs = [spec.margin + grid_w/2]
    else:
        for i in range(spec.cols):
            xs.append(spec.margin + (grid_w * i) / (spec.cols - 1))
    if spec.rows == 1:
        ys = [spec.margin + grid_h/2]
    else:
        for j in range(spec.rows):
            ys.append(spec.margin + (grid_h * j) / (spec.rows - 1))
    centers = [(x,y) for y in ys for x in xs]
    return centers

def draw_holes(msp, centers: List[Tuple[float,float]], dia: float):
    r = dia / 2.0
    for (x,y) in centers:
        msp.add_circle((x,y), r, dxfattribs={"layer": "HOLES"})

def annotate(msp, spec: PartSpec):
    note = f"{spec.name}: {spec.length}x{spec.width} mm"
    if spec.rows and spec.cols and spec.hole_diameter:
        note += f" | holes {spec.rows}x{spec.cols} Ø{spec.hole_diameter} mm, m={spec.margin}"
    if spec.thickness:
        note += f" | t={spec.thickness} mm"
    if spec.material:
        note += f" | {spec.material}"
    # Place note near top-right corner with small offset
    x = spec.length + 5
    y = spec.width - 5
    msp.add_text(
    note,
    dxfattribs={"height": spec.text_height, "layer": "ANNOTATIONS"}
).set_dxf_attrib("insert", (x, y))


def save_dxf(doc, out_path: Path):
    doc.saveas(out_path)

def export_spec_to_dxf(spec: PartSpec, out_dir: Path = OUT_DIR) -> Path:
    spec.validate()
    doc = create_new_doc()
    msp = doc.modelspace()
    draw_plate(msp, spec.length, spec.width)
    centers = hole_centers(spec)
    if centers:
        draw_holes(msp, centers, spec.hole_diameter)
    annotate(msp, spec)
    out_file = out_dir / build_filename(spec)
    save_dxf(doc, out_file)
    return out_file

def maybe_draw_live_in_autocad(spec: PartSpec):
    if not spec.draw_live:
        return
    Autocad, APoint = _try_import_autocad()
    if Autocad is None:
        print("Live draw skipped: pyautocad/AutoCAD not available. DXF still generated.", file=sys.stderr)
        return
    try:
        acad = Autocad(create_if_not_exists=True)
        # Draw same geometry in the active document
        def L(p1, p2):
            acad.model.AddLine(APoint(*p1), APoint(*p2))
        def C(center, r):
            acad.model.AddCircle(APoint(*center), r)
        # plate
        L((0,0), (spec.length,0))
        L((spec.length,0), (spec.length,spec.width))
        L((spec.length,spec.width), (0,spec.width))
        L((0,spec.width), (0,0))
        # holes
        for (x,y) in hole_centers(spec):
            C((x,y), spec.hole_diameter/2.0)
        print("Live drawing sent to AutoCAD.")
    except Exception as e:
        print(f"Live draw failed: {e}", file=sys.stderr)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate parametric DXF plates with hole grids.")
    p.add_argument("--name", default="plate", help="Part name used in note and filename")
    p.add_argument("--length", type=float, help="Plate length in mm")
    p.add_argument("--width", type=float, help="Plate width in mm")
    p.add_argument("--margin", type=float, default=10.0, help="Uniform margin around hole grid in mm")
    p.add_argument("--hole_diameter", type=float, default=0.0, help="Hole diameter in mm (0 => no holes)")
    p.add_argument("--rows", type=int, default=0, help="Number of hole rows (0 => no holes)")
    p.add_argument("--cols", type=int, default=0, help="Number of hole columns (0 => no holes)")
    p.add_argument("--material", default="", help="Material note, e.g., MS/Al/SS")
    p.add_argument("--thickness", type=float, default=0.0, help="Thickness note in mm")
    p.add_argument("--text_height", type=float, default=3.0, help="Annotation text height in mm")
    p.add_argument("--csv", type=str, help="CSV path for batch generation")
    p.add_argument("--draw_live", action="store_true", help="Also send geometry to live AutoCAD (Windows + AutoCAD)")
    return p.parse_args()

def run_single_from_args(ns: argparse.Namespace) -> Optional[Path]:
    if ns.length is None or ns.width is None:
        print("ERROR: --length and --width are required for single-part mode (or use --csv).", file=sys.stderr)
        return None
    spec = PartSpec(
        name=ns.name,
        length=ns.length,
        width=ns.width,
        margin=ns.margin,
        hole_diameter=ns.hole_diameter,
        rows=ns.rows,
        cols=ns.cols,
        material=ns.material,
        thickness=ns.thickness,
        text_height=ns.text_height,
        draw_live=ns.draw_live,
    )
    path = export_spec_to_dxf(spec, OUT_DIR)
    maybe_draw_live_in_autocad(spec)
    print(f"DXF written: {path}")
    return path

def run_csv(csv_path: Path) -> List[Tuple[int, Optional[Path], Optional[str]]]:
    results = []
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):  # header is line 1
            try:
                spec = PartSpec(
                    name=(row.get("name") or "part").strip(),
                    length=float(row["length"]),
                    width=float(row["width"]),
                    margin=float(row.get("margin", 10) or 10),
                    hole_diameter=float(row.get("hole_diameter", 0) or 0),
                    rows=int(row.get("rows", 0) or 0),
                    cols=int(row.get("cols", 0) or 0),
                    material=(row.get("material") or "").strip(),
                    thickness=float(row.get("thickness", 0) or 0),
                )
                path = export_spec_to_dxf(spec, OUT_DIR)
                results.append((idx, path, None))
            except Exception as e:
                results.append((idx, None, str(e)))
    for (line, path, err) in results:
        if err:
            print(f"Line {line}: SKIPPED → {err}")
        else:
            print(f"Line {line}: OK → {path}")
    return results

def main():
    ns = parse_args()
    if ns.csv:
        csv_path = Path(ns.csv).resolve()
        if not csv_path.exists():
            print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
            sys.exit(2)
        run_csv(csv_path)
    else:
        if run_single_from_args(ns) is None:
            sys.exit(2)

if __name__ == "__main__":
    main()
