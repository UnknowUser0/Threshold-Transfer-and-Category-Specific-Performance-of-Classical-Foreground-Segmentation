# CDnet2014 IJCCS Research Package

This package contains the audited CDnet2014 study and a manuscript draft targeting the Indonesian Journal of Computing and Cybernetics Systems (IJCCS). It does not include raw benchmark videos or masks.

## Start here

- `START_HERE.md` — project overview and commands
- `paper/MANUSCRIPT_MASTER.docx` — Word manuscript draft formatted to IJCCS page/font settings
- `paper/MANUSCRIPT_MASTER.md` — editable manuscript source
- `paper/IJCCS_Journal_Template.doc` — official legacy Word template
- `paper/IJCCS_GUIDELINES.md` — author-format checklist
- `paper/AUTHOR_METADATA_FORM.md` and `paper/IJCCS_COVER_LETTER_DRAFT.md` — author completion materials
- `SUBMISSION_GATE.md` — remaining actions before submission
- `DATASET_PROVENANCE.md` — locally validated dataset counts and distribution note
- `FINAL_AUDIT.json` — integrity and metric audit

The primary 320-pixel results are frozen. Temporal and resolution follow-ups were run post-hoc on three selected sequences and are descriptive only. No modern-model scores are presented because a fair, exposure-controlled comparison could not be established with the available training provenance.

The local dataset contained 11 categories, 53 sequences, and 159,278 input frames. It was used for local validation and follow-up studies but is excluded from this archive. Obtain CDnet2014 from its official source and follow its terms before rerunning.

## IJCCS format

The official instructions call for English manuscript text; bilingual abstracts of at most 200 words each; 10–12 Letter pages; 3 cm margins; single spacing; Times New Roman 11 pt body, 18 pt title, 11 pt italic abstracts; one column; at least 10 IEEE-style references with URLs, including 80% primary references. The DOCX structure matches the page and font settings, but final page count and visual layout must be checked in Microsoft Word.

Official venue sources checked 22 November 2026:

- Author instructions: https://journal.ugm.ac.id/ijccs/about/submissions
- SINTA profile: https://sinta.kemdiktisaintek.go.id/journals/profile/1075

## Reproduce

From this folder, use the configured Python environment with the packages in `requirements.txt`:

```powershell
python run_final.py audit
python run_final.py tests
python run_final.py temporal --dataset "D:\Datasets\CDnet2014"
python run_final.py resolution --dataset "D:\Datasets\CDnet2014" --widths 320 640 native
```

The temporal/resolution commands write post-hoc outputs beneath `working/final-*`. Existing frozen results are not overwritten. Do not treat pilot frames as independent statistical units.

## Submission status

Author identities, affiliations, email/ORCID, funding, competing interests, contributions, and final coauthor approval must be supplied by the authors. Independently verify any preregistration-timing claim. The current environment does not render Microsoft Word pagination. Journal review and acceptance cannot be guaranteed.
