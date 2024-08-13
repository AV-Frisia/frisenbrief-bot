import pypandoc

from pylatexenc.latexencode import unicode_to_latex
import textract
import chardet
import tempfile
import subprocess
import logging


def convert(file_format, file_content):
    """Convert a string to a LaTeX string"""

    # File Format is critical for conversion
    if not file_format:
        return

    # Skip conversion if file is already tex
    if file_format.lower() == "tex":
        return str(file_content)

    latex = ""

    # use pypandoc for all supported types
    if file_format in pypandoc.get_pandoc_formats()[0]:
        latex += pypandoc.convert_text(file_content, format=file_format, to="latex")
    elif file_format.lower() in ["txt"]:
        # Detect encoding (because fucking Notepad.exe doesn't do UTF-8 until Build 1903)
        en = chardet.detect(file_content)["encoding"]
        latex += unicode_to_latex(
            file_content.decode(encoding=en),
            unknown_char_policy="ignore",
            unknown_char_warning=False,
        )
    else:
        # Textract wants a "regular" file
        tmp = tempfile.NamedTemporaryFile(suffix="." + file_format)
        tmp.write(file_content)

        # mainly PDFs or older .doc's
        text = textract.process(tmp.name, language="deu")
        latex = "% Achtung: Formatierung war nicht möglich.\r\n"
        latex += unicode_to_latex(
            text.decode(), unknown_char_policy="ignore", unknown_char_warning=False
        )

    return latex


def touchup(file: str):
    """Runs final touches (such as formatting) on a LaTeX file"""
    subprocess.run(["latexindent", file, "-s", "-m", "-o", file], check=True)
    return file
