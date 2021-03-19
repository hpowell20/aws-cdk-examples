from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticsearch as es,
    aws_ssm as ssm
)


from aws_cdk.core import Construct, CfnOutput, Duration, RemovalPolicy, Stack, Tags

CERT_ARN_SSM_KEY_NAME = 'base-certificate-arn'


class ElasticsearchDomainStack(Stack):

    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read in the details of the VPC
        vpc = ec2.Vpc.from_lookup(self, "VPC",
            vpc_id=vpc_id
        )

        # Create a security group for the domain
        es_access_sg = ec2.SecurityGroup(self, id="es_access_sg",
            vpc=vpc,
            security_group_name=f"{stage_name}-es-access-sg"
        )

        Tags.of(es_access_sg).add('Name', 'Elasticsearch Domain Instance Access Security Group')

        # Adds an ingress rule which allows resources in the VPC's CIDR
        # to access the domain
        es_access_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(443)
        )

        es_access_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443)
        )

        # Lookup the certificate ARN - This must be the one in the us-east-1 region
        cert_arn = ssm.StringParameter.value_for_string_parameter(
            self, CERT_ARN_SSM_KEY_NAME)

        # Set the Elasticsearch domain options
        domain_name = f"{stage_name}-es-domain"
        instance = es.Domain(self, "EsDomain",
            domain_name=domain_name,
            version=es.ElasticsearchVersion.V7_9,
            ebs=es.EbsOptions(
                volume_size=100,
                volume_type=ec2.EbsDeviceVolumeType.GP3
            ),
            encryption_at_rest=es.EncryptionAtRestOptions(
                enabled=True,
            )
        )
        
        # Set the stack outputs
        CfnOutput(self, "SecurityGroupId",
            value=es_access_sg.security_group_id,
            description='The security group used to manage access to Elasticsearch',
            export_name=f"{stage_name}-SecurityGroupId")
        CfnOutput(self, "DomainArn", value=instance.domain_arn)
        CfnOutput(self, "DomainEndpoint",
            value=instance.domain_endpoint,
            description='The domain-specific endpoint that is used to submit index, search, and data upload requests to an Amazon ES domain',
            export_name=f"{stage_name}-DomainName")
