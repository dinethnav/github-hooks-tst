import os
from datetime import datetime, timezone

import requests

base_url = os.environ["CONFLUENCE_BASE_URL"]
email = os.environ["CONFLUENCE_EMAIL"]
api_token = os.environ["CONFLUENCE_API_TOKEN"]
page_id = os.environ["CONFLUENCE_PAGE_ID"]

repo = os.environ["REPO_NAME"]
pr_number = os.environ["PR_NUMBER"]
pr_title = os.environ["PR_TITLE"]
pr_url = os.environ["PR_URL"]
branch = os.environ["BRANCH_NAME"]
commit = os.environ["COMMIT_SHA"][:7]

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

auth = (email, api_token)

# Read page
response = requests.get(
    f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage,version",
    auth=auth,
)
response.raise_for_status()

page = response.json()

title = page["title"]
version = page["version"]["number"]
body = page["body"]["storage"]["value"]

new_row = f"""
<tr>
    <td>{repo}</td>
    <td><a href="{pr_url}">#{pr_number} - {pr_title}</a></td>
    <td>{branch}</td>
    <td><code>{commit}</code></td>
    <td>✅ Passed</td>
    <td>{timestamp}</td>
</tr>
"""

if "</tbody>" not in body:
    raise Exception(
        "No table found. Please create the CI/CD Dashboard table first."
    )

updated_body = body.replace("</tbody>", f"{new_row}\n</tbody>", 1)

payload = {
    "id": page_id,
    "type": "page",
    "title": title,
    "version": {
        "number": version + 1,
    },
    "body": {
        "storage": {
            "value": updated_body,
            "representation": "storage",
        }
    },
}

update = requests.put(
    f"{base_url}/wiki/rest/api/content/{page_id}",
    auth=auth,
    headers={"Content-Type": "application/json"},
    json=payload,
)

update.raise_for_status()

print("Successfully updated Confluence dashboard.")