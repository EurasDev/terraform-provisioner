docker build -t terraform-python:1.0.0 .

docker login

docker tag terraform-python:1.0.0 jackamatic/terraform-python:1.0.0

docker push jackamatic/terraform-python:1.0.0