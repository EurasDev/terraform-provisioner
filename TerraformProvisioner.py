import os
import subprocess
import argparse
import tempfile

class TerraformProvisioner:

    def __init__(self, working_dir, aws_profile=None):
        self.working_dir = working_dir
        if aws_profile:
            os.environ["AWS_PROFILE"] = aws_profile

    def _run_terraform_command(self, command):
        try:
            result = subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error executing Terraform command: {e}")
            return None

    def init(self):
        command = ["terraform", "init"]
        print(f"Terraform initialised")
        return self._run_terraform_command(command)


    def workspace(self, workspace_name=None):
        if workspace_name:
            command = ["terraform", "workspace", "select", workspace_name]
            print(f"Workspace selected: {workspace_name}")
            return self._run_terraform_command(command)

    def plan(self, var_files=None, plan_file=None):
        command = ["terraform", "plan"]

        if var_files:
            for var_file in var_files:
                var_file = f"{var_file}.tfvars"
                command.extend(["-var-file", var_file])
                print(f"Var file defined: {var_file}")
        else:
            print(f"No var file defined, continuing...")

        if plan_file:
            command.extend(["-out", plan_file])

        plan_success = self._run_terraform_command(command)
        return plan_success

    def apply(self, var_files=None, workspace_name=None):
        self.init()
        self.workspace(workspace_name)

        plan_success = self.plan(var_files)
            
        if plan_success:
            print(f"Active workspace: {workspace_name}")
            input("Press Enter to apply changes or CTRL+C to interrupt!")
            command = ["terraform", "apply"]
            if var_files:
                for var_file in var_files:
                    var_file = f"{var_file}.tfvars"
                    command.extend(["-var-file", var_file])
            return self._run_terraform_command(command)
        else:
            print("Error during planning. Skipping apply step.")

    def destroy(self, var_files=None, workspace_name=None):
        self.init()
        self.workspace(workspace_name)

        print("Planning destroy:")
        command = ["terraform", "plan", "-destroy"]
        if var_files:
            for var_file in var_files:
                var_file = f"{var_file}.tfvars"
                command.extend(["-var-file", var_file])
        plan_output = self._run_terraform_command(command)

        if not plan_output:
            print("Error during destroy planning. Skipping destroy step.")
            return

        print(f"Active workspace: {workspace_name}")
        input("Press Enter to continue with the destroy or CTRL+C to interrupt!")
        
        command = ["terraform", "destroy"]
        if var_files:
            for var_file in var_files:
                var_file = f"{var_file}.tfvars"
                command.extend(["-var-file", var_file])
        return self._run_terraform_command(command)

    def validate(self):
        command = ["terraform", "validate"]
        return self._run_terraform_command(command)
        
def main():
    parser = argparse.ArgumentParser(description='A script to manage Terraform projects.')
    parser.add_argument('-d', '--directory', dest="directory", required=True, help='Terraform working directory')
    parser.add_argument('-p', '--profile',dest="profile", default="tf", help='AWS profile to use')
    parser.add_argument('-w', '--workspace', dest="workspace", default="default", help='Terraform workspace to use (optional)')
    parser.add_argument('-v', '--var-file', dest="var_file", action='append', default=[], help='Terraform variable file (optional)')
    parser.add_argument('--destroy', action='store_true', help='Run terraform destroy')
    parser.add_argument('--plan', action='store_true', help='Run terraform plan only, do not apply or destroy')
    parser.add_argument('--validate', action='store_true', help='Run terraform validate only')

    args = parser.parse_args()
    tf_provisioner = TerraformProvisioner(args.directory, aws_profile=args.profile)

    try:
        if args.validate:
            tf_provisioner.validate()
        elif args.plan:
            tf_provisioner.init()
            tf_provisioner.workspace(args.workspace)
            tf_provisioner.plan(var_files=args.var_file)
        elif args.destroy:
            tf_provisioner.destroy(var_files=args.var_file, workspace_name=args.workspace)
        else:
            tf_provisioner.apply(var_files=args.var_file, workspace_name=args.workspace)
    except KeyboardInterrupt:
        print("\nCancelled by user. Exiting...")

if __name__ == "__main__":
    main()