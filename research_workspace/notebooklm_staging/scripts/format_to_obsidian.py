import os
import shutil
from datetime import datetime
from pathlib import Path

# Define Paths
STAGING_DIR = Path(__file__).resolve().parent.parent / "02_extracted_insights"
OBSIDIAN_VAULT = Path(__file__).resolve().parent.parent.parent / "obsidian_vault" / "01_mathematical_models"

def create_obsidian_note(file_path: Path):
    """Reads raw NotebookLM output and formats it into an Obsidian-ready markdown file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract a clean title from the filename
    title = file_path.stem.replace("_", " ").title()
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. Inject Obsidian YAML Frontmatter for graphing and searchability
    yaml_frontmatter = f"""---
title: "{title}"
date_ingested: {date_str}
tags: [notebooklm, literature_review, unprocessed_model]
status: In_Review
---
"""

    # 2. Append the Axiom Alpha Translation Template to the bottom
    axiom_template = """
---
## 🛠 Axiom Implementation Strategy

### 1. Theoretical Objective
*What specific market noise does this model decouple?*

### 2. Core Mathematical Formulation
$$
% Write the core reward function or causal graph math here %
$$

### 3. Engineering Dependencies
* **Target Module:** `src/engine/`
* **Data Required:** 
* **Compute Node:** PC GPU / Lenovo Data Node

### 4. Next Steps
- [ ] Open GitHub Issue for Implementation
- [ ] Draft PyTorch Architecture
"""

    # Combine everything
    final_markdown = f"{yaml_frontmatter}\n# NotebookLM Summary: {title}\n\n{content}\n{axiom_template}"

    # Define the new path inside the Obsidian Vault
    dest_path = OBSIDIAN_VAULT / f"{title.replace(' ', '_')}.md"
    
    # Ensure the target directory exists
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)

    # Write the formatted file to the Vault
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)

    print(f"✅ Processed and moved to Vault: {dest_path.name}")
    
    # Delete the raw file from staging to keep it clean
    os.remove(file_path)

def run_pipeline():
    print("Scanning for new NotebookLM insights...")
    processed_count = 0
    
    for file in os.listdir(STAGING_DIR):
        if file.endswith(".txt") or file.endswith(".md"):
            file_path = STAGING_DIR / file
            create_obsidian_note(file_path)
            processed_count += 1
            
    if processed_count == 0:
        print("No new insights found in staging.")
    else:
        print(f"🎉 Pipeline complete. {processed_count} notes bridged to Obsidian.")

if __name__ == "__main__":
    run_pipeline()