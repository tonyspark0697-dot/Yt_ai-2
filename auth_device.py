"""One-time YouTube login that works from a PHONE (no browser on this machine needed).

Run it anywhere with Python (Termux, Google Colab, a GitHub Codespace), type your OAuth
client ID/secret, then approve on your phone at google.com/device.
It prints TOKEN_B64, which you paste into GitHub as a repository secret.

The OAuth client must be of type "TVs and Limited Input devices".
"""
import base64
import json
import sys
import time

import requests

SCOPE = "https://www.googleapis.com/auth/youtube"


def main():
    cid = input("OAuth Client ID: ").strip()
    secret = input("OAuth Client secret: ").strip()

    r = requests.post("https://oauth2.googleapis.com/device/code",
                      data={"client_id": cid, "scope": SCOPE}, timeout=30).json()
    if "device_code" not in r:
        sys.exit(f"Could not start login: {r}")
    print(f"\n1) On your phone open:  {r['verification_url']}")
    print(f"2) Enter this code:     {r['user_code']}")
    print("3) Choose the Google account that owns your YouTube channel and allow access.\n")

    interval, deadline = r.get("interval", 5), time.time() + r["expires_in"]
    while time.time() < deadline:
        time.sleep(interval)
        t = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": cid, "client_secret": secret, "device_code": r["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}, timeout=30).json()
        if "access_token" in t:
            break
        err = t.get("error")
        if err == "slow_down":
            interval += 5
        elif err != "authorization_pending":
            sys.exit(f"Login failed: {t}")
    else:
        sys.exit("Timed out waiting for approval. Run again.")

    if not t.get("refresh_token"):
        sys.exit("Google did not return a refresh token. Remove the app at "
                 "myaccount.google.com/permissions and run again.")
    token = {"token": t["access_token"], "refresh_token": t["refresh_token"],
             "token_uri": "https://oauth2.googleapis.com/token",
             "client_id": cid, "client_secret": secret, "scopes": [SCOPE]}
    raw = json.dumps(token).encode()
    open("token.json", "wb").write(raw)
    print("\nLogin OK. Copy everything below into the GitHub secret named TOKEN_B64:\n")
    print(base64.b64encode(raw).decode())
    print("\nKeep it private: it gives access to your YouTube channel.")


if __name__ == "__main__":
    main()
