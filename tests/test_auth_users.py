def test_register_login_list_users(client):
    r = client.post("/api/auth/register", json={"username":"tester","password":"Pass123!","role":"staff"})
    assert r.status_code in (200,201)
    r = client.post("/api/auth/login", json={"username":"tester","password":"Pass123!"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (200,403)
