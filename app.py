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

