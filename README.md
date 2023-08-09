docker build -t terraform-python:1.0.0 .

docker login

docker tag terraform-python:1.0.0 jackamatic/terraform-python:1.0.0

docker push jackamatic/terraform-python:1.0.0

./run_me.sh -d ../Terraform-Docker-Project/ --plan

If code changes aren't taking effect, run docker system prune -a