@"
# scripts/test_auth_flow.py
"""
Simple end-to-end auth flow tester for SPMS backend.
Adjust BASE_URL and ADMIN_PASSWORD if needed.
"""
import time
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/auth"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"   # dev default created at startup
TEST_USERNAME = "autotest_user"
TEST_PASSWORD = "Test@12345"
NEW_PASSWORD = "NewTest@12345"

def form_login(username, password):
    url = f"{BASE_URL}/login"
    data = {"username": username, "password": password}
    return requests.post(url, data=data)

def json_post(path, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{BASE_URL}{path}", json=payload, headers=headers)

def admin_post(path, token, payload=None):
    headers = {"Authorization": f"Bearer {token}"}
    if payload:
        headers["Content-Type"] = "application/json"
        return requests.post(f"{BASE_URL}{path}", json=payload, headers=headers)
    return requests.post(f"{BASE_URL}{path}", headers=headers)

def main():
    print("1) Register test user (idempotent)")
    payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "full_name": "Auto Test",
        "email": "autotest@example.com",
        "role": "staff"
    }
    r = json_post("/register", payload)
    print("  register:", r.status_code, r.text)
    if r.status_code not in (200, 201):
        print("  (continuing; user may already exist)")

    print("2) Login as admin to get admin token")
    r = form_login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if r.status_code != 200:
        print("Admin login failed:", r.status_code, r.text)
        sys.exit(1)
    admin_tokens = r.json()
    admin_token = admin_tokens.get("access_token")
    print("  admin token acquired")

    print("3) Ensure test user can login (correct password)")
    r = form_login(TEST_USERNAME, TEST_PASSWORD)
    print("  login:", r.status_code, r.text)
    if r.status_code == 200:
        user_token = r.json().get("access_token")
        print("  test user login OK")
    else:
        print("  test user login failed (may be locked or not created)")

    print("4) Force failed logins to trigger lockout (6 attempts)")
    for i in range(1, 7):
        r = form_login(TEST_USERNAME, "wrongpassword")
        print(f"  attempt {i}: {r.status_code}")
        time.sleep(0.2)

    print("5) Try correct password after lockout")
    r = form_login(TEST_USERNAME, TEST_PASSWORD)
    print("  after lockout attempt:", r.status_code, r.text)

    print("6) Admin unlock test user via API")
    r = admin_post(f"/admin/unlock-account/{TEST_USERNAME}", admin_token)
    print("  admin unlock:", r.status_code, r.text)

    print("7) Try login again with correct password")
    r = form_login(TEST_USERNAME, TEST_PASSWORD)
    print("  login after admin unlock:", r.status_code, r.text)
    if r.status_code == 200:
        user_token = r.json().get("access_token")
        print("  login success after unlock")

    print("8) Admin reset password for test user")
    r = admin_post(f"/admin/reset-password/{TEST_USERNAME}", admin_token, {"new_password": NEW_PASSWORD})
    print("  reset password:", r.status_code, r.text)

    print("9) Login with new password")
    r = form_login(TEST_USERNAME, NEW_PASSWORD)
    print("  login with new password:", r.status_code, r.text)

    print("Done.")

if __name__ == "__main__":
    main()
