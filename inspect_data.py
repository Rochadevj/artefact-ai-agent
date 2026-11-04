from pathlib import Path

import pandas as pd
from pypdf import PdfReader


DATA_DIR = Path("data")


def inspect_csv_files():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    print(f"\nCSV files found: {len(csv_files)}")

    for csv_file in csv_files:
        print("\n" + "=" * 60)
        print(f"File: {csv_file.name}")

        df = pd.read_csv(csv_file)

        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

        print("\nFirst 3 rows:")
        print(df.head(3).to_string(index=False))


def inspect_pdf_files():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    print(f"\nPDF files found: {len(pdf_files)}")

    for pdf_file in pdf_files:
        print("\n" + "=" * 60)
        print(f"File: {pdf_file.name}")

        reader = PdfReader(pdf_file)

        print(f"Pages: {len(reader.pages)}")

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        print("\nText preview:")
        print(text[:3000])


if __name__ == "__main__":
    inspect_csv_files()
    inspect_pdf_files()