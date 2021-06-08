import json

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secrets,
    aws_ssm as ssm,
)

from aws_cdk.core import Construct, CfnOutput, Duration, RemovalPolicy, Stack, Tags


class RdsStack(Stack):

    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str,
                 vpc_ref: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the security group for instance
        rds_access_sg = ec2.SecurityGroup(self, id='rds_access_sg',
                                          vpc=vpc_ref,
                                          security_group_name=f'{stage_name}-db-access-sg')

        Tags.of(rds_access_sg).add('Name', 'Database Instance Access Security Group')

        # Adds an ingress rule which allows resources in the VPC's CIDR
        # to access the database
        rds_access_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(5432)
        )

        # TODO: Change these values depending on dev, prod, etc.
        instance_type = ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL)
        allocated_storage = 25
        multi_az = False
        storage_encrypted = False
        backup_retention = Duration.days(0)  # Disabled for non prod environments
        delete_automated_backups = True
        deletion_protection = False

        # Create the database credentials
        database_name = 'test_db'
        master_username = 'postgres'

        secret_name = f'{project_code}/{stage_name}/Postgres'
        db_credentials_secret = secrets.Secret(self, id=f'{stage_name}-db-credentials-secret',
                                               removal_policy=RemovalPolicy.DESTROY,
                                               secret_name=secret_name,
                                               generate_secret_string=secrets.SecretStringGenerator(
                                                   secret_string_template=json.dumps({'username': master_username}),
                                                   exclude_punctuation=True,
                                                   include_space=False,
                                                   generate_string_key='password'
                                               ))

        # Store the secret key name in SSM
        key_name = f"{project_code}-{stage_name}-db-secret-name"
        ssm.StringParameter(self, 'DbCredentialsSecretName',
                            parameter_name=key_name,
                            string_value=secret_name)

        instance = rds.DatabaseInstance(self, "PostgresInstance",
                                        database_name=database_name,
                                        credentials=rds.Credentials.from_secret(db_credentials_secret),
                                        instance_identifier=f'{project_code}-{stage_name}-postgres',
                                        engine=rds.DatabaseInstanceEngine.postgres(
                                            version=rds.PostgresEngineVersion.VER_13_1
                                        ),
                                        auto_minor_version_upgrade=True,
                                        storage_encrypted=storage_encrypted,
                                        backup_retention=backup_retention,
                                        vpc=vpc_ref,
                                        vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                        security_groups=[rds_access_sg],
                                        instance_type=instance_type,
                                        allocated_storage=allocated_storage,
                                        storage_type=rds.StorageType.GP2,
                                        removal_policy=RemovalPolicy.DESTROY,
                                        multi_az=multi_az,
                                        delete_automated_backups=delete_automated_backups,
                                        deletion_protection=deletion_protection)

        # Rotate the master user password every 30 days
        instance.add_rotation_single_user(
            exclude_characters='!@#$%^&*'
        )

        # instance.connections.allow_internally(ec2.Port.all_tcp(), 'All traffic within security group')

        # Set the stack outputs
        CfnOutput(self, "InstanceArn", value=instance.instance_arn)
        CfnOutput(self, "InstanceIdentifier", value=instance.instance_identifier)
        CfnOutput(self, "InstanceEndpoint", value=instance.db_instance_endpoint_address)

        # Prepares output attributes to be passed into other stacks
        self._instance = instance

    @property
    def instance_ref(self) -> rds.IDatabaseInstance:
        return self._instance
