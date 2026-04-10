"""Sync access.yaml allowed_emails to the Cloudflare Access policy for this app."""
import os
import sys
import yaml
import requests

token      = os.environ["CLOUDFLARE_API_TOKEN"]
account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
app_id     = os.environ["CLOUDFLARE_APP_ID"]
policy_id  = os.environ["CLOUDFLARE_POLICY_ID"]

with open("access.yaml") as f:
    config = yaml.safe_load(f)

emails = config.get("allowed_emails", [])
if not emails:
    print("No allowed_emails found in access.yaml — aborting to avoid locking everyone out.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
url = (
    f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
    f"/access/apps/{app_id}/policies/{policy_id}"
)

resp = requests.put(url, headers=headers, json={
    "name": "Allow list",
    "decision": "allow",
    "include": [{"email": {"email": e}} for e in emails],
})
resp.raise_for_status()
print(f"✓ Policy updated — {len(emails)} email(s) allowed")
