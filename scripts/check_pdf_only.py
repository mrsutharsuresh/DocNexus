import time
import requests
import sys

API_URL = "http://127.0.0.1:5000"

def wait_for_server(timeout=30):
    print("Waiting for server...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{API_URL}/debug/info", timeout=1)
            if resp.status_code == 200:
                print(f"Server Up! Version: {resp.json().get('version')}")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def test_pdf_export():
    print(f"Testing PDF Export...")
    payload = {"html": "<h1>Hello World from Automated Test</h1><p>Checking reportlab dependencies.</p>"}
    try:
        resp = requests.post(f"{API_URL}/api/export/pdf", json=payload, timeout=20)
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print(f"SUCCESS: PDF Generated (Size: {len(resp.content)} bytes)")
                return True
            else:
                print(f"FAILURE: Wrong Content-Type: {content_type}")
                return False
        else:
            print(f"FAILURE: Status {resp.status_code}")
            print(f"Response: {resp.text}")
            return False
    except Exception as e:
        print(f"FAILURE: Request Exception: {e}")
        return False

if __name__ == "__main__":
    if wait_for_server():
        if test_pdf_export():
            sys.exit(0)
    sys.exit(1)
