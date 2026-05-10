# Axiom Alpha: Literature Ingestion SOP

## Phase 1: Sourcing (The Drop)
1. Download papers (.pdf) from ArXiv, SSRN, or internal sources.
2. Drop them into `01_raw_papers/`.
3. Run `python scripts/standardize_pdfs.py` to strip out messy web characters and standardize the naming convention.

## Phase 2: NotebookLM Synthesis
1. Open Google NotebookLM in the browser.
2. Create a new notebook (e.g., "Causal RL May 2026").
3. Upload the standardized PDFs from `01_raw_papers/`.
4. Generate the "Audio Overview" (Podcast) and download the `.wav`/`.mp3` to `02_extracted_insights/`.
5. Prompt NotebookLM to generate a "Comprehensive Mathematical and Architectural Summary" of the uploaded papers. 
6. Copy that text and save it as a raw `.txt` or `.md` file in `02_extracted_insights/`.

## Phase 3: The Obsidian Bridge
1. Run `python scripts/format_to_obsidian.py`.
2. This script will automatically consume the raw summaries, inject YAML frontmatter, append the Axiom `Model_Translation_Template`, and move the final files directly into the `obsidian_vault`.