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
        previous_cwd = os.getcwd()
        os.chdir(self.working_dir)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing Terraform command: {e}")
            print(e.stderr)
            return None
        finally:
            os.chdir(previous_cwd)


    def init(self):
        command = ["terraform", "init"]
        return self._run_terraform_command(command)


    def workspace(self, workspace_name=None):
        if workspace_name:
            command = ["terraform", "workspace", "select", workspace_name]
            return self._run_terraform_command(command)


    def plan(self, var_files=None, plan_file=None):
        command = ["terraform", "plan"]

        if var_files:
            for var_file in var_files:
                command.extend(["-var-file", var_file])

        if plan_file:
            command.extend(["-out", plan_file])

        plan_output = self._run_terraform_command(command)
        if plan_output:
            return plan_output
        else:
            print("Error during planning.")


    def apply(self, var_files=None, workspace_name=None):
        self.init()
        self.workspace(workspace_name)
        
        with tempfile.NamedTemporaryFile() as plan_file:
            plan_output = self.plan(var_files, plan_file.name)
            if plan_output:
                print(f"Active workspace: {workspace_name}")
                input("Press Enter to apply changes or CTRL+C to interrupt!")
                command = ["terraform", "apply", "-auto-approve", plan_file.name]
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
                command.extend(["-var-file", var_file])
        plan_output = self._run_terraform_command(command)
        if plan_output:
            print(f"Active workspace: {workspace_name}")
            input("Press Enter to destroy resources or CTRL+C to interrupt!")
            command = ["terraform", "destroy", "-auto-approve"]
            if var_files:
                for var_file in var_files:
                    command.extend(["-var-file", var_file])
            return self._run_terraform_command(command)
        else:
            print("Error during destroy planning. Skipping destroy step.")

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