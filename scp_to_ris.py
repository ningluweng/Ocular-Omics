import csv
import html
import re

INPUT_CSV = "sca_file.csv"
OUTPUT_RIS = "sca_output.ris"

def clean_text(value):
    """
    Clean text from the CSV:
    - Handle None
    - Strip leading/trailing whitespace
    - Decode HTML entities
    - Collapse internal whitespace to single spaces
    """
    if value is None:
        return ""
    text = str(value).strip()
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_sca_csv():
    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f_in, \
         open(OUTPUT_RIS, "w", encoding="utf-8", newline="\n") as out:

        reader = csv.DictReader(f_in)

        for row in reader:
            accession = clean_text(row.get("Accession", ""))
            name = clean_text(row.get("Name", ""))
            description = clean_text(row.get("Description", ""))
            study_url = clean_text(row.get("Study URL", ""))
            disease = clean_text(row.get("Disease", ""))
            organ = clean_text(row.get("Organ", ""))
            species = clean_text(row.get("Species", ""))
            library_prep = clean_text(row.get("Library preparation protocol", ""))
            facet_matches = clean_text(row.get("Facet matches", ""))

            # Skip rows with no accession
            if not accession:
                continue

            # Title: Name [Facet matches] [Species]
            title_parts = [name]
            if facet_matches:
                title_parts.append(f"[{facet_matches}]")
            if species:
                title_parts.append(f"[{species}]")
            title = " ".join(title_parts)

            # Start RIS record
            out.write("TY  - JOUR\n")

            if title:
                out.write(f"TI  - {title}\n")

            # Authors:
            # Author 1: Accession (e.g., SCP1311)
            # Author 2: Library preparation protocol
            # Author 3: Disease
            authors = [accession]
            if library_prep:
                authors.append(library_prep)
            if disease:
                authors.append(disease)

            for author in authors:
                out.write(f"AU  - {author}\n")

            # Publication (Journal)
            out.write("JO  - Single Cell Portal\n")

            # DOI = Study URL
            if study_url:
                out.write(f"DO  - {study_url}\n")

            # Abstract = Description
            if description:
                out.write(f"AB  - {description}\n")

            # End of record
            out.write("ER  - \n\n")

    print(f"Done. Wrote RIS file to: {OUTPUT_RIS}")

if __name__ == "__main__":
    process_sca_csv()
