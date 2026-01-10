import requests

# Login
response = requests.post(
    "http://127.0.0.1:8000/auth/login",
    data={
        "username": "admin",
        "password": "admin123"
    }
)

if response.status_code == 200:
    data = response.json()
    print("✅ Login successful!")
    print(f"Access Token: {data['access_token']}")
    print(f"\nToken Type: {data['token_type']}")
else:
    print(f"❌ Login failed: {response.text}")