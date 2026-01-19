import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone

# --- YOUR DETAILS ---
YOUR_NAME = "MOHD TUFAIL KHAN"
YOUR_EMAIL = "tufailkhan.contact@gmail.com"
# Since you don't have a resume, we are using a placeholder.
# The application will send successfully, but there is no real resume attached.
RESUME_LINK = "https://linkedin.com/in/placeholder" 
# --------------------

def main():
    # 1. Get the secret and GitHub info
    signing_secret = os.environ.get("B12_SIGNING_SECRET") 
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    
    # 2. Build the links
    repo_link = f"{server_url}/{repo}"
    action_run_link = f"{repo_link}/actions/runs/{run_id}"
    
    # 3. Get the time (ISO 8601 format)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 4. Create the data packet
    payload_dict = {
        "timestamp": timestamp,
        "name": YOUR_NAME,
        "email": YOUR_EMAIL,
        "resume_link": RESUME_LINK,
        "repository_link": repo_link,
        "action_run_link": action_run_link
    }

    # 5. Format the data (Canonical JSON)
    payload_json = json.dumps(payload_dict, sort_keys=True, separators=(',', ':'))
    print(f"Sending Payload: {payload_json}")

    # 6. Sign the data (HMAC-SHA256)
    if not signing_secret:
        print("Error: Secret is missing.")
        exit(1)

    signature = hmac.new(
        key=signing_secret.encode('utf-8'),
        msg=payload_json.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 7. Send to B12
    url = "https://b12.io/apply/submission"
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}"
    }

    try:
        response = requests.post(url, data=payload_json, headers=headers)
        
        # 8. Check if it worked
        if response.status_code == 200:
            print("\nSUCCESS! Application Submitted.")
            print(f"Receipt: {response.json().get('receipt')}")
        else:
            print(f"\nFAILED. Server responded: {response.status_code}")
            print(response.text)
            exit(1)

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
