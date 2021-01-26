from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds
)

from aws_cdk.core import Construct, CfnOutput, Duration, RemovalPolicy, SecretValue, Stack, Tags


class RdsStack(Stack):

    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the security group for instance
        rds_access_sg = ec2.SecurityGroup(self, id="rds_access_sg",
            vpc=props['vpc'],
            security_group_name=f"{stage_name}-db-access-sg"
        )

        Tags.of(rds_access_sg).add('Name', 'Database Instance Access Security Group')

        # Adds an ingress rule which allows resources in the VPC's CIDR
        # to access the database
        rds_access_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(5432)
        )

        # TODO: Remove the all rule
        rds_access_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(5432)
        )

        # TODO: Change these values depending on dev, prod, etc.
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MEDIUM)
        allocated_storage=25
        multi_az=False
        storage_encrypted=False
        backup_retention=Duration.days(0) # Disabled for non prod enviroments
        delete_automated_backups=True
        deletion_protection=False

        # Create the RDS instance
        identifier = f"servus-{stage_name}-postgres"

        # TODO: Create a random password and set secrets manager values
        master_username = 'postgres'
        master_password = self.node.try_get_context("default_master_password")

        instance = rds.DatabaseInstance(self, "PostgresInstance",
            instance_identifier=identifier,
            credentials=rds.Credentials.from_username(master_username,
                            password=SecretValue.plain_text(master_password)),
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12_3
            ),
            auto_minor_version_upgrade=False,
            storage_encrypted=storage_encrypted,
            backup_retention=backup_retention,
            vpc=props['vpc'],
            vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[rds_access_sg],
            instance_type=instance_type,
            allocated_storage=allocated_storage,
            storage_type=rds.StorageType.GP2,
            removal_policy=RemovalPolicy.DESTROY,
            multi_az=multi_az,
            delete_automated_backups=delete_automated_backups,
            deletion_protection=deletion_protection
        )

        # Set the stack outputs
        CfnOutput(self, "InstanceArn", value=instance.instance_arn)
        CfnOutput(self, "InstanceIdentifier", value=instance.instance_identifier)
        CfnOutput(self, "InstanceEndpoint", value=instance.db_instance_endpoint_address)
