import io
import re
import csv
import base64
from typing import List, Dict, Tuple, Optional
import streamlit as st
import fitz # PyMuPDF
from pyzbar.pyzbar import decode as zbar_decode
from PIL import Image
import pandas as pd

#-----------------------------------
# Heuristics & Regex
#-----------------------------------

PHONE_RE = re.compile(r"(\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}")
APT_RE = re.compile(r"(?:Apt|Apartment|Suite|Ste|#)\s*[A-Za-z0-9\-]+", re.IGNORECASE)

# Rudimentary address line: number + street + suffix (very permissive)
ADDR_LINE_RE = re.compile(
    r"^\s*(\d{1,6}\s+.+)$"
)
CITY_ST_RE = re.compile(
    r"\b([A-Za-z\.\-\s]+?),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b"
)

def render_page_to_image(page: fitz.Page, zoom: float = 2.0) -> Image.Image:
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def extract_words(page: fitz.Page):
    """"Return words with positions: list of (x0, y0, x1, y1, word)"""
    words = page.get_text("words") # x0, y0, x1, y1, word, block_no, word_no
    words = [(w[0], w[1], w[2], w[3], w[4], w[5], w[6]) for w in words] # keep block/line no
    return words

def group_lines(words, y_tol=4):
    """Group words into lines by line_no: returns list of dicts with text and bbox."""
    lines = {}
    for (x0,y0,x1,y1,word,block_no,line_no) in words:
        key = (block_no, line_no)
        if key not in lines:
            lines[key] = {"text": [], "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                          "block_no": block_no, "line_no": line_no}

        else:
            lines[key]["x0"] = min(lines[key]["x0"], x0)
            lines[key]["y0"] = min(lines[key]["y0"], y0)
            lines[key]["x1"] = min(lines[key]["x1"], x1)
            lines[key]["y1"] = min(lines[key]["y1"], y1)
        lines[key["text"].append(word)]
    # convert to list, join text
    out = []
    for k in sorted(lines.key(), key=lambda k: (lines[k]["y0"], lines[k]["x0"])):
        it = lines[key]
        it["text"] = " ".join(it["text"]).strip()
        out.append(it)
    return out
