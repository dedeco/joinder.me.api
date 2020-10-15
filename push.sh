#!/bin/sh
echo 'Up lovers microservices....'
cp ci/config/lover/cloudbuild.yaml cloudbuild.yaml
cp ci/config/lover/Dockerfile Dockerfile
gcloud builds submit --config cloudbuild.yaml .

echo 'Up contents microservices....'
cp ci/config/content/cloudbuild.yaml cloudbuild.yaml
cp ci/config/content/Dockerfile Dockerfile
gcloud builds submit --config cloudbuild.yaml .

echo 'Up chat microservices....'
cp ci/config/chat/cloudbuild.yaml cloudbuild.yaml
cp ci/config/chat/Dockerfile Dockerfile
gcloud builds submit --config cloudbuild.yaml .

echo 'Up profiles microservices....'
cp ci/config/profile/cloudbuild.yaml cloudbuild.yaml
cp ci/config/profile/Dockerfile Dockerfile
gcloud builds submit --config cloudbuild.yaml .

echo 'Up user microservices....'
cp ci/config/user/cloudbuild.yaml cloudbuild.yaml
cp ci/config/user/Dockerfile Dockerfile
gcloud builds submit --config cloudbuild.yaml .