# Database Deployment #

This project is used to create the database storage resources.  Services used includes:

- Custom VPC
- Postgres RDS instance
- Database access security groups

### Project Structure ##

- The `cdk.json` file tells the CDK Toolkit how to execute the application
- The `setup.py` file defines the modules required to deploy the resources
- The `app.py` file runs the commands required to deploy the stack

NOTE:

- To add additional dependencies (i.e. - other CDK libraries) simply add them to the `requirements.txt` file and rerun the `pip install -r requirements.txt` command

### NPM Dependencies ###

Ensure the AWS CDK is installed

```
npm install -g aws-cdk
```

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
cdk synth -c stage_name=test
```

** NOTES: **

- Replace **test** with your assume role profile name

Run the script to create the environment

```
export AWS_PROFILE=test
export AWS_ACCOUNT=123456789
export AWS_REGION=ca-central-1
./deploy-env.sh <stage_name>
```

** NOTES: **

- Replace **test** with your assume role profile name
- Replace **123456789** with the AWS account ID
- Please include your name for the stage name if you want to create custom AWS stack for testing purposes

### Remove Existing Stack ###

Run the script to destroy the environment

```
export AWS_PROFILE=test
export AWS_ACCOUNT=123456789
export AWS_REGION=ca-central-1
./remove-env.sh <stage_name>
```

** NOTES: **

- Replace **test** with your assume role profile name
- Replace **123456789** with the AWS account ID
- Please include your name for the stage name if you want to create custom AWS stack for testing purposes

### Useful commands ###

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation
