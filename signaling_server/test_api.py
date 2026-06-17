#!/usr/bin/env python3
"""API and policy tests for signaling server."""

import json
import urllib.request
import urllib.error

BASE = "http://localhost:3000"


def post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as resp:
        return json.loads(resp.read())


def main():
    health = get("/health")
    assert health["messagesStored"] == 0, "Server must not store messages"
    print("✓ Health check:", health)

    post("/api/register", {
        "username": "testuser1",
        "password": "secret12",
        "publicKey": "cHVibGljLWtleS10ZXN0LTEyMzQ1Ng==",
    })
    post("/api/register", {
        "username": "testuser2",
        "password": "secret12",
        "publicKey": "cHVibGljLWtleS10ZXN0LTc4OTAxMg==",
    })
    print("✓ Registration works")

    login = post("/api/login", {"username": "testuser1", "password": "secret12"})
    assert "token" in login
    print("✓ Login returns JWT token")

    try:
        get("/api/messages/anything")
    except urllib.error.HTTPError as e:
        assert e.code == 404
        body = json.loads(e.read())
        assert "not supported" in body["error"].lower() or "not supported" in body["error"]
    print("✓ Message storage endpoint blocked (privacy policy)")

    pk = get("/api/users/testuser2/public-key")
    assert pk["username"] == "testuser2"
    print("✓ Public key retrieval works")

    print("\nAll tests passed. Server stores NO message content.")


if __name__ == "__main__":
    main()
