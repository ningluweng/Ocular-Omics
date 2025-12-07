import csv
import html
import re

INPUT_CSV = "dbgap.csv"   # change this if your file is named differently
OUTPUT_RIS = "dbgap_output.ris"

def clean_text(value):
    """
    Clean text from the CSV:
    - Handle None
    - Strip leading/trailing whitespace
    - Decode HTML entities (e.g., &#x02011;)
    - Collapse internal whitespace to single spaces
    - Treat 'Not Provided' and 'Not Applicable' as empty
    """
    if value is None:
        return ""
    text = str(value).strip()
    if text in ("Not Provided", "Not Applicable", ""):
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_dbgap_csv():
    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f_in, \
         open(OUTPUT_RIS, "w", encoding="utf-8", newline="\n") as out:

        reader = csv.DictReader(f_in)

        for row in reader:
            accession = clean_text(row.get("accession", ""))
            name = clean_text(row.get("name", ""))
            description = clean_text(row.get("description", ""))

            study_content = clean_text(row.get("Study Content", ""))
            disease = clean_text(row.get("Study Disease/Focus", ""))
            study_design = clean_text(row.get("Study Design", ""))
            markerset = clean_text(row.get("Study Markerset", ""))
            mol_type = clean_text(row.get("Study Molecular Data Type", ""))
            release_date = clean_text(row.get("Release Date", ""))

            # Skip rows with no accession at all
            if not accession:
                continue

            # Title: Name [Study Content]
            if study_content:
                title = f"{name} [{study_content}]"
            else:
                title = name

            year = ""
            if release_date and len(release_date) >= 4:
                year = release_date[:4]

            out.write("TY  - JOUR\n")

            if title:
                out.write(f"TI  - {title}\n")

            # Authors: accession, then disease/design/markerset/molecular type (if present)
            authors = [accession]
            for v in (disease, study_design, markerset, mol_type):
                if v:
                    authors.append(v)

            for author in authors:
                out.write(f"AU  - {author}\n")

            out.write("JO  - dbGAP\n")

            if year:
                out.write(f"PY  - {year}\n")
            if release_date:
                out.write(f"DA  - {release_date}\n")

            if description:
                out.write(f"AB  - {description}\n")

            out.write("ER  - \n\n")

    print(f"Done. Wrote RIS file to: {OUTPUT_RIS}")

if __name__ == "__main__":
    process_dbgap_csv()
