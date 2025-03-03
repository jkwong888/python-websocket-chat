# simple python websocket chat

## tracing -> langfuse

1. install langfuse v2 on cloud run (v3 instructions soon) > [docs](https://langfuse.com/self-hosting/v2/deployment-guide#google-cloud-platform-cloud-run--cloud-sql)

```
gcloud beta run deploy langfuse \
--image=langfuse/langfuse:2 \
--allow-unauthenticated \
--port=3000 \
--service-account=<sa_email> \
--cpu=2 \
--memory=4Gi \
--max-instances=2 \
--set-env-vars=DATABASE_HOST=<cloud sql ip> \
--set-env-vars='NEXTAUTH_URL=https://langfuse.gcp.jkwong.info' \
--set-env-vars='NEXTAUTH_SECRET=<openssl rand -base64 32>' \
--set-env-vars=SALT=<openssl rand -base64 32> \
--set-env-vars=ENCRYPTION_KEY=$(openssl rand -hex 32) \
--set-env-vars=HOSTNAME=0.0.0.0 \
--set-env-vars=DATABASE_USERNAME=postgres \
--set-env-vars='^#^DATABASE_PASSWORD=<password>' \
--set-env-vars=DATABASE_NAME=postgres \
--set-cloudsql-instances=<cloud sql instand id>> \
--network=projects/jkwng-nonprod-vpc/global/networks/shared-vpc-nonprod-1 \
--subnet=projects/jkwng-nonprod-vpc/regions/us-central1/subnetworks/langfuse-dev \
--vpc-egress=all-traffic \
--no-cpu-throttling \
--execution-environment=gen2 \
--ingress=internal-and-cloud-load-balancing \
--region=us-central1 \
--project=jkwng-langfuse
```

2. log into langfuse, create a user, org, and project (you may want to block signups)


## deploy to cloud run

1. docker build -t <your repo> .
2. docker push <your repo>
3. deploy to cloud run, e.g.

```
gcloud beta run deploy python-websocket-chat \
--image=gcr.io/jkwng-images/python-websocket-chat:latest \
--set-env-vars='MY_WS_URL=wss://python-websocket-chat.gcp.jkwong.info/ws' \
--set-env-vars='LANGFUSE_HOST=https://langfuse.gcp.jkwong.info' \
--set-env-vars=LANGFUSE_PUBLIC_KEY=<public key> \
--set-env-vars=LANGFUSE_SECRET_KEY=<secret key> \
--execution-environment=gen2 \
--region=us-central1 \
--project=jkwng-vertex-playground \
 && gcloud run services update-traffic python-websocket-chat --to-latest
```

## call synchronous API

see the code in [sa_creds_client.py](sa_creds_client.py) for signing token for services behind IAP or cloud run authentication.# python-websocket-chat
