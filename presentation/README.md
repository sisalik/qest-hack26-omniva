# Presentation

The slides are written in Markdown with [Marp](https://marp.app/). `slides.md` is the whole deck; slides are separated by `---`.

## Requirements (from the organizers)

5 minutes + 2 minutes Q&A, delivered as **Google Slides**:

1. Business problem (1 min): why it is hard, how many qubits the full (not toy) problem needs, circuit scaling (linear or quadratic?)
2. Results, numbers and graphs (2.5 min)
3. Lessons learned (1 min)
4. Next steps (30 s)

Each slide has its time budget in the speaker notes (`<!-- ... -->` blocks).

## Editing and preview

- Install the VS Code extension **Marp for VS Code** (`marp-team.marp-vscode`).
- Open `slides.md` and click the preview icon in the top right corner: the slides update as you type.
- Orange `[…]` placeholders mark what still needs to be filled in.
- Put images (plots exported from the notebooks) in `img/` and reference them as `![w:900](img/name.png)`.

## Export to Google Slides

```bash
cd presentation
npx @marp-team/marp-cli@latest slides.md --pptx -o slides.pptx
```

Then upload `slides.pptx` to Google Drive and open it with Google Slides.

By default each slide is exported as an image, so text cannot be edited in Google Slides (speaker notes are kept). For editable text, add `--pptx-editable` (experimental, requires LibreOffice). PDF or HTML for a quick check: replace `--pptx` with `--pdf` or `--html`.

Exported files (`*.pptx`, `*.pdf`, `*.html`) are build outputs and are not committed.
