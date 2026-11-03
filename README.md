# Clemency tracker

A sourced dataset of US presidential clemency actions, plus the build script that renders it to a
printable PDF table.

- `trump_clemency.csv` — **513 rows**, one per grant, with name, date, type (pardon / commutation),
  category, offence, original sentence, restitution, court, term, source URL and a verification status.
- `rows.json` — the same records normalised for rendering.
- `build.py` — normalises dates and names, generates `index.html`.
- `make_pdf.py` — renders the HTML to `trump_clemency.pdf`.

## Notes on the data

`Source_URL` is populated per row and `Verification_Status` records whether the entry was confirmed
against a primary source. Rows where restitution or political party are unknown say `Unknown` rather than
guessing — the blanks are deliberate.

## Rebuilding

```
python3 build.py        # csv + rows.json -> index.html
python3 make_pdf.py     # index.html -> trump_clemency.pdf
```
