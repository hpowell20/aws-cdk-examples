from aws_cdk import aws_ec2 as ec2

from aws_cdk.core import Construct, CfnOutput, Stack


class VpcStack(Stack):
    def __init__(self, scope: Construct, id: str, stage_name: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Subnet configurations for a public and private tier
        public_subnet = ec2.SubnetConfiguration(
            name="Public",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24)
        private_subnet = ec2.SubnetConfiguration(
            name="Private",
            subnet_type=ec2.SubnetType.PRIVATE,
            cidr_mask=24)
        db_subnet = ec2.SubnetConfiguration(
            name="DB",
            subnet_type=ec2.SubnetType.ISOLATED,
            cidr_mask=24)

        # Create the VPC
        vpc_name = f"{stage_name}-custom-vpc"
        vpc = ec2.Vpc(self, vpc_name,
                      cidr="10.0.0.0/16",
                      max_azs=2,
                      enable_dns_hostnames=True,
                      enable_dns_support=True,
                      subnet_configuration=[public_subnet, private_subnet, db_subnet],
                      nat_gateways=2)

        # Set the stack outputs
        CfnOutput(self, "VpcId", value=vpc.vpc_id, export_name=vpc_name)
