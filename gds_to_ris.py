#!/usr/bin/env python3
"""
GDS to RIS Converter
This script parses a GDS text file and 
converts each numbered entry to RIS format.
"""

import re
import sys

def parse_gds_entry(entry_text):
    """
    Parse a single GDS entry and extract relevant fields.

    Args:
        entry_text: String containing a single GDS entry

    Returns:
        Dictionary with parsed fields
    """
    # Extract title (first line after number)
    title_match = re.match(r'^\d+\.\s+(.+?)$', entry_text.split('\n')[0])
    title = title_match.group(1).strip() if title_match else ""

    # Extract abstract (submitter supplied text)
    abstract_match = re.search(r'\(Submitter supplied\)\s+(.+?)(?=Organism:|$)', entry_text, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else ""
    # Remove "more..." if present
    abstract = re.sub(r'\s*more\.\.\.\s*$', '', abstract)

    # Extract organism
    organism_match = re.search(r'Organism:\s*(.+?)$', entry_text, re.MULTILINE)
    organism = organism_match.group(1).strip() if organism_match else ""

    # Extract platform info
    platform_match = re.search(r'Platform[s]?:\s*(.+?)$', entry_text, re.MULTILINE)
    platform = platform_match.group(1).strip() if platform_match else ""

    # Extract FTP download URL
    ftp_match = re.search(r'FTP download:.*?(ftp://[^\s]+)', entry_text)
    ftp_url = ftp_match.group(1).strip() if ftp_match else ""

    # Extract Series Accession
    accession_match = re.search(r'Accession:\s*(GSE\d+)', entry_text)
    accession = accession_match.group(1).strip() if accession_match else ""

    # Extract Series ID
    id_match = re.search(r'ID:\s*(\d+)', entry_text)
    series_id = id_match.group(1).strip() if id_match else ""

    # Extract SRA Run Selector if present
    sra_match = re.search(r'SRA Run Selector:\s*(https?://[^\s]+)', entry_text)
    sra_url = sra_match.group(1).strip() if sra_match else ""

    return {
        'title': title,
        'abstract': abstract,
        'organism': organism,
        'platform': platform,
        'ftp_url': ftp_url,
        'accession': accession,
        'series_id': series_id,
        'sra_url': sra_url
    }

def create_ris_entry(parsed_data):
    """
    Create a RIS format entry from parsed data.

    Args:
        parsed_data: Dictionary with parsed fields

    Returns:
        String in RIS format
    """
    ris_lines = []

    # Type of reference - Journal Article
    ris_lines.append("TY  - JOUR")

    # Title - append organism in brackets
    if parsed_data['title']:
        title_with_organism = f"{parsed_data['title']}"
        if parsed_data['organism']:
            title_with_organism += f" [{parsed_data['organism']}]"
        ris_lines.append(f"TI  - {title_with_organism}")

    # Authors - using accession numbers and platform info as per example
    if parsed_data['accession']:
        ris_lines.append(f"AU  - {parsed_data['accession']}")

    if parsed_data['series_id']:
        ris_lines.append(f"AU  - {parsed_data['series_id']}")

    if parsed_data['platform']:
        ris_lines.append(f"AU  - {parsed_data['platform']}")

    # Journal/Publication name
    ris_lines.append("JO  - Gene Expression Omnibus")

    # DOI field - using FTP URL as per example
    if parsed_data['ftp_url']:
        ris_lines.append(f"DO  - {parsed_data['ftp_url']}")

    # Abstract
    if parsed_data['abstract']:
        ris_lines.append(f"AB  - (Submitter supplied) {parsed_data['abstract']}")

    # URL - if SRA URL exists, add it
    if parsed_data['sra_url']:
        ris_lines.append(f"UR  - {parsed_data['sra_url']}")

    # End of record
    ris_lines.append("ER  - ")
    ris_lines.append("")  # Empty line between entries

    return "\n".join(ris_lines)

def parse_gds_file(input_file):
    """
    Parse the entire GDS file and split into individual entries.

    Args:
        input_file: Path to input GDS text file

    Returns:
        List of entry strings
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by numbered entries (1., 2., 3., etc.)
    # This regex splits on newline followed by number and period
    entries = re.split(r'(?=^\d+\.\s+)', content, flags=re.MULTILINE)

    # Filter out empty entries
    entries = [e.strip() for e in entries if e.strip()]

    return entries

def main():
    """Main function to convert GDS to RIS format."""
    if len(sys.argv) < 2:
        print("Usage: python gds_to_ris.py <input_file.txt> [output_file.ris]")
        print("\nIf output file is not specified, will create 'output.ris'")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.ris"

    print(f"Reading from: {input_file}")
    print(f"Writing to: {output_file}")
    print()

    # Parse the input file
    entries = parse_gds_file(input_file)
    print(f"Found {len(entries)} entries")
    print()

    # Convert each entry to RIS format
    ris_entries = []
    for i, entry in enumerate(entries, 1):
        parsed = parse_gds_entry(entry)
        ris_entry = create_ris_entry(parsed)
        ris_entries.append(ris_entry)

        if i <= 3:  # Show first 3 entries as examples
            print(f"Entry {i}: {parsed['title'][:50]}...")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(ris_entries))

    print()
    print(f"✓ Successfully converted {len(entries)} entries to RIS format")
    print(f"✓ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
