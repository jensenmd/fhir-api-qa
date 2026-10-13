"""Render the editable SVG card. Requires CairoSVG and native Cairo."""
from pathlib import Path
import cairosvg

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    cairosvg.svg2png(url=str(root / "assets/project-card.svg"),
                    write_to=str(root / "fhir-api-qa-project-card.png"),
                    output_width=1200, output_height=630)
