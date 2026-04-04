"""
Manual test script for the Document Analysis API.
Tests the POST /api/document-analyze endpoint with various file types and error cases.

Usage:
    python test_api.py [API_URL] [API_KEY]

Examples:
    python test_api.py
    python test_api.py http://localhost:8000
    python test_api.py https://my-deploy.example.com my_secret_key
"""

import base64
import json
import os
import sys

import requests

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_API_KEY = "hcl_hack_api_key_2024_secure"

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_config():
    """Parse optional CLI args for API URL and API key."""
    api_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_API_URL
    api_key = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_API_KEY
    # Strip trailing slash
    api_url = api_url.rstrip("/")
    return api_url, api_key


def pretty_print(label, response):
    """Pretty-print an HTTP response."""
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception:
        print(f"Raw body: {response.text[:500]}")
    print()


def make_request(api_url, api_key, payload, extra_headers=None):
    """Send a POST to /api/document-analyze and return the response."""
    url = f"{api_url}/api/document-analyze"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    return requests.post(url, headers=headers, json=payload, timeout=60)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def build_sample_pdf_base64():
    """Build a minimal PDF in memory and return its base64 encoding.

    This creates a bare-bones valid PDF without any third-party library so the
    test script stays dependency-light.
    """
    # Minimal valid PDF with some text content for analysis
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 184 >>\nstream\n"
        b"BT\n/F1 12 Tf\n72 720 Td\n"
        b"(Acme Corporation Quarterly Report - Q3 2024.) Tj\n"
        b"0 -20 Td\n"
        b"(Revenue reached $2.5 billion, up 15 percent year over year.) Tj\n"
        b"0 -20 Td\n"
        b"(CEO John Smith announced expansion plans on October 15, 2024.) Tj\n"
        b"ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000280 00000 n \n"
        b"0000000518 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n598\n%%EOF\n"
    )
    return base64.b64encode(pdf_content).decode("utf-8")


def test_sample_pdf(api_url, api_key):
    """Test with an in-memory minimal PDF."""
    print(">> Testing with sample PDF (in-memory) ...")
    payload = {
        "fileName": "sample_report.pdf",
        "fileType": "pdf",
        "fileBase64": build_sample_pdf_base64(),
    }
    resp = make_request(api_url, api_key, payload)
    pretty_print("Sample PDF Analysis", resp)
    return resp


def test_file(api_url, api_key, file_path, file_type):
    """Test with a real file from disk."""
    print(f">> Testing with file: {file_path} (type={file_type}) ...")
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    file_name = os.path.basename(file_path)
    payload = {
        "fileName": file_name,
        "fileType": file_type,
        "fileBase64": encoded,
    }
    resp = make_request(api_url, api_key, payload)
    pretty_print(f"File Analysis: {file_name}", resp)
    return resp


def test_all_file_types(api_url, api_key):
    """Look for sample files of each supported type and test them."""
    type_map = {
        "pdf": [".pdf"],
        "docx": [".docx"],
        "image": [".png", ".jpg", ".jpeg"],
    }
    tested = set()
    for file_type, extensions in type_map.items():
        for ext in extensions:
            # Look for any matching file in the project directory
            for fname in os.listdir(SAMPLE_DIR):
                if fname.lower().endswith(ext):
                    fpath = os.path.join(SAMPLE_DIR, fname)
                    if os.path.isfile(fpath) and file_type not in tested:
                        test_file(api_url, api_key, fpath, file_type)
                        tested.add(file_type)
                        break

    if not tested:
        print("(No sample pdf/docx/image files found in project directory.)")
    else:
        print(f"Tested file types from disk: {', '.join(sorted(tested))}")


# ---------------------------------------------------------------------------
# Error-case tests
# ---------------------------------------------------------------------------

def test_missing_api_key(api_url):
    """POST without the x-api-key header."""
    print(">> Testing missing API key ...")
    url = f"{api_url}/api/document-analyze"
    payload = {
        "fileName": "test.pdf",
        "fileType": "pdf",
        "fileBase64": build_sample_pdf_base64(),
    }
    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    pretty_print("Error: Missing API Key", resp)
    if resp.status_code in (401, 403):
        print("  [PASS] Server correctly rejected request without API key.")
    else:
        print(f"  [WARN] Expected 401/403 but got {resp.status_code}.")
    return resp


def test_invalid_api_key(api_url):
    """POST with a wrong API key."""
    print(">> Testing invalid API key ...")
    payload = {
        "fileName": "test.pdf",
        "fileType": "pdf",
        "fileBase64": build_sample_pdf_base64(),
    }
    resp = make_request(api_url, "totally_wrong_key_12345", payload)
    pretty_print("Error: Invalid API Key", resp)
    if resp.status_code in (401, 403):
        print("  [PASS] Server correctly rejected invalid API key.")
    else:
        print(f"  [WARN] Expected 401/403 but got {resp.status_code}.")
    return resp


def test_invalid_base64(api_url, api_key):
    """POST with garbage base64 content."""
    print(">> Testing invalid base64 ...")
    payload = {
        "fileName": "bad_file.pdf",
        "fileType": "pdf",
        "fileBase64": "!!!NOT_VALID_BASE64!!!",
    }
    resp = make_request(api_url, api_key, payload)
    pretty_print("Error: Invalid Base64", resp)
    if resp.status_code >= 400:
        print(f"  [PASS] Server returned error status {resp.status_code}.")
    else:
        print(f"  [WARN] Expected an error status but got {resp.status_code}.")
    return resp


def test_unsupported_file_type(api_url, api_key):
    """POST with a file type the API does not support."""
    print(">> Testing unsupported file type ...")
    payload = {
        "fileName": "data.csv",
        "fileType": "csv",
        "fileBase64": base64.b64encode(b"col1,col2\n1,2\n").decode("utf-8"),
    }
    resp = make_request(api_url, api_key, payload)
    pretty_print("Error: Unsupported File Type", resp)
    if resp.status_code >= 400:
        print(f"  [PASS] Server returned error status {resp.status_code}.")
    else:
        print(f"  [WARN] Expected an error status but got {resp.status_code}.")
    return resp


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_url, api_key = get_config()
    print(f"API URL : {api_url}")
    print(f"API Key : {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else f"API Key : {api_key}")
    print()

    # --- Happy path ---
    print("=" * 60)
    print("  HAPPY-PATH TESTS")
    print("=" * 60)

    test_sample_pdf(api_url, api_key)
    test_all_file_types(api_url, api_key)

    # --- Error cases ---
    print("=" * 60)
    print("  ERROR-CASE TESTS")
    print("=" * 60)

    test_missing_api_key(api_url)
    test_invalid_api_key(api_url)
    test_invalid_base64(api_url, api_key)
    test_unsupported_file_type(api_url, api_key)

    print("\n" + "=" * 60)
    print("  ALL TESTS FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    main()
