###
#
# Signs JWT tokens for requests to a cloud run service that is behind IAP or requires service account authentication
#
###

import requests
import json

from datetime import datetime, timezone, timedelta

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

sa_email = "webchat-client@jkwng-vertex-playground.iam.gserviceaccount.com"
service_url = "https://python-websocket-chat.gcp.jkwong.info/generate"
aud = service_url

# authenticate GCP
creds, project = google.auth.default(scopes="https://googleapis.com/auth/cloud-platform")
auth_req = google.auth.transport.requests.Request()

creds.refresh(auth_req)# generate the JWT using this REST API call
sa_creds_url = f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{sa_email}:signJwt"

def getToken(aud=aud, sub=sa_email):
    # generate a JWT to be signed
    jwt_payload = {
        "iss": sa_email,
        "sub": sub,
        "aud": aud,
        "iat": round((datetime.now(tz=timezone.utc)).timestamp()),
        "exp": round((datetime.now(tz=timezone.utc) + timedelta(minutes=5)).timestamp()),
    }

    req_payload = {
        "payload": json.dumps(jwt_payload),
    }

    response = requests.post(
        url=sa_creds_url,
        data=json.dumps(req_payload),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {creds.token}"
        }
    )

    signed_jwt = response.json()['signedJwt']

    return signed_jwt

token = getToken()
#time.sleep(1)

queryStr = """
What are five potential use cases for AI?
"""

queryObj = {
    "query": queryStr
}

for i in range(1000):
    response = requests.post(
        url=service_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        data=json.dumps(queryObj)

    )

    print(f"{response.status_code} {response.json()}")

