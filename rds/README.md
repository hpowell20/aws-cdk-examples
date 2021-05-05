# Database Deployment #

This project is used to create the database storage resources.  Services used includes:

- VPC
- Postgres RDS instance
- Database access security groups

### Project Structure ##

- The `cdk.json` file tells the CDK Toolkit how to execute the application
- The `setup.py` file defines the modules required to deploy the resources
- The `app.py` file runs the commands required to deploy the stack

NOTE:

- To add additional dependencies (i.e. - other CDK libraries) simply add them to the `requirements.txt` file and rerun the `pip install -r requirements.txt` command

### Python Dependencies ###

Ensure the prerequisites are installed

```
- Python3.8
- pip (tool for installing Python packages)
```

Create virtual env for python3.8 inside project directory:

```
python3.8 -m venv venv
```

Activate newly created environment

```
. venv/bin/activate (Linux / OSX)
.env\Scripts\activate.bat (Windows)
```

Install the required python packages

```
pip install -r requirements.txt
```

### Deploy New Stack ###

Synthesize the CloudFormation template

```
npx cdk synth -c stage_name=test
```

** NOTES: **

- Replace **test** with your assume role profile name

Run the script to create the environment

```
export AWS_PROFILE=<profile_name>
export AWS_ACCOUNT=<account_id>
export AWS_REGION=<region_name>
./deploy-env.sh <stage_name>
```

** NOTE: **
- Replace values with your account details

### Remove Existing Stack ###

Run the script to destroy the environment

```
export AWS_PROFILE=<profile_name>
export AWS_ACCOUNT=<account_id>
export AWS_REGION=<region_name>
./remove-env.sh <stage_name>
```

** NOTE: **
- Replace values with your account details

### Useful commands ###

- `npx cdk ls` list all stacks in the app
- `npx cdk synth` emits the synthesized CloudFormation template
- `npx cdk deploy` deploy this stack to your default AWS account/region
- `npx cdk diff` compare deployed stack with current state
- `npx cdk docs` open CDK documentation
