FROM hashicorp/terraform:latest

WORKDIR /workspace

RUN apk add --update --no-cache python3

COPY TerraformProvisioner.py /provisioner/TerraformProvisioner.py

ENTRYPOINT [ "/bin/sh" ]