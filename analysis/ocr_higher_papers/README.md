# OCR Higher past-paper analysis (chronology step 72)

One-off analysis tooling, **not part of the app**. See CLAUDE.md step 72 for the full story.

- Source papers: 33 OCR J560 Higher question papers (Papers 4/5/6, June 2017 – June 2025) in
  `C:\Users\James\Downloads\` (file → sitting map is the `FILES` dict in `prox_locate.py`, plus
  `locate.py` for the recurring-decimal subset).
- Master tag data: the **"Topic tags" sheet of `Downloads\OCR_Higher_Topic_Analysis_Detailed.xlsx`**
  (1,553 rows: part × topic, with sub-type, structure, style, AO, position, app coverage). The
  original `tags.txt`/`deep_*.txt` scratch files were lost when the temp scratchpad was cleared —
  the workbook is the surviving source of truth.
- Topic packs (questions cropped as vector content from the user's own PDFs + verified answers):
  - `build_recurring_pdf.py` (+ `locate.py`, `crops.py`, `loc.json`) → `Downloads\OCR_Higher_Recurring_Decimals.pdf`
  - `build_prox_pdf.py` (+ `prox_locate.py`, `prox_items.py`) → `Downloads\OCR_Higher_Algebraic_Proportion.pdf`
- Run with the backend venv from this folder; `build_*_pdf.py` add `backend/` to `sys.path` to reuse
  `app.pdf.mathtext.to_markup` for fractions/recurring dots in the answers.
- The packs reproduce OCR's copyrighted questions — personal classroom use only, never commit the
  PDFs or publish them.
