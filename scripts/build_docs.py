import pypandoc
import os

DOC_SOURCE = "docs/LIVE_PROJECT_BOOK.md"
HTML_OUT = "docs/LIVE_PROJECT_BOOK.html"
DOCX_OUT = "docs/LIVE_PROJECT_BOOK.docx"

def build_docs():
    if not os.path.exists(DOC_SOURCE):
        raise FileNotFoundError("LIVE_PROJECT_BOOK.md not found.")

    # Convert to HTML
    pypandoc.convert_file(
        DOC_SOURCE,
        "html",
        outputfile=HTML_OUT,
        extra_args=["--standalone"]
    )

    # Convert to Word
    pypandoc.convert_file(
        DOC_SOURCE,
        "docx",
        outputfile=DOCX_OUT,
        extra_args=["--standalone"]
    )

    print("Documentation built successfully.")

if __name__ == "__main__":
    build_docs()
