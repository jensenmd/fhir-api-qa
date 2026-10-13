# Portfolio card

The editable source is [project-card.svg](project-card.svg). It reconstructs the 1200 × 630 layout of the reference `restful-booker-qa-project-card.png`; no editable template was present in the inspected reference repositories.

The SVG retains the reference layout, dark background, blue/green/purple accents, badges, footer, and three-stage diagram, with FHIR-specific labels. It uses Arial; font rendering can vary by system.

From the repository root:

```bash
python -m pip install -r assets/requirements.txt
python assets/render_card.py
```

Rendering requires CairoSVG and native Cairo. Windows installations may need Cairo DLLs on PATH. The script writes `fhir-api-qa-project-card.png` in the repository root.
