from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticsearch as es,
    aws_iam as iam
)


from aws_cdk.core import Construct, CfnOutput, RemovalPolicy, Stack, Tags


class ElasticsearchDomainStack(Stack):

    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read in the details of the VPC
        vpc = ec2.Vpc.from_lookup(self, "VPC",
                                  vpc_id=vpc_id)

        # Create a security group for the domain
        es_access_sg = ec2.SecurityGroup(self, id="es_access_sg",
                                         vpc=vpc,
                                         security_group_name=f"{project_code}-{stage_name}-es-access-sg")

        Tags.of(es_access_sg).add('Name', 'Elasticsearch Domain Instance Access Security Group')

        # Adds an ingress rule which allows resources in the VPC's CIDR
        # to access the domain
        es_access_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(443)
        )

        CfnOutput(self, "SecurityGroupId",
                  value=es_access_sg.security_group_id,
                  description='The security group used to manage access to Elasticsearch',
                  export_name=f"{stage_name}-SecurityGroupId")

        # Set the Elasticsearch domain options
        domain_name = f"{project_code}-{stage_name}-es-domain"

        # TODO: Update to set for production clusters
        capacity_config = es.CapacityConfig(
            data_node_instance_type='t3.small.elasticsearch',
            data_nodes=1,
            master_node_instance_type=None,
            master_nodes=None,
            warm_instance_type=None,
            warm_nodes=None,
        )

        ebs_options = es.EbsOptions(
            volume_size=100,
            volume_type=ec2.EbsDeviceVolumeType.GP2
        )

        access_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            principals=[iam.AnyPrincipal()],
            actions=['es:ESHttp*'],
            resources=[f'arn:aws:es:{self.region}:{self.account}:domain/{domain_name}/*']
        )

        zone_awareness = es.ZoneAwarenessConfig(
            availability_zone_count=None,
            enabled=False,
        )

        # TODO: When setting to True fine grained access control needs to be enabled
        logging_options = es.LoggingOptions(
            app_log_enabled=False,
            audit_log_enabled=False,
            slow_index_log_enabled=False,
            slow_search_log_enabled=False
        )

        # TODO: Pull the subnets from the VPC using the export name
        # subnets=[]

        instance = es.Domain(self, "EsDomain",
                             domain_name=domain_name,
                             removal_policy=RemovalPolicy.DESTROY,
                             version=es.ElasticsearchVersion.V7_10,
                             enable_version_upgrade=True,
                             capacity=capacity_config,
                             ebs=ebs_options,
                             access_policies=[access_policy],
                             zone_awareness=zone_awareness,
                             logging=logging_options,
                             automated_snapshot_start_hour=10,
                             security_groups=[es_access_sg],
                             # vpc_subnets=subnets,
                             node_to_node_encryption=True,
                             encryption_at_rest=es.EncryptionAtRestOptions(
                                 enabled=True,
                             ))
        
        # Set the stack outputs
        CfnOutput(self, "DomainArn", value=instance.domain_arn)
        CfnOutput(self, "DomainEndpoint",
                  value=instance.domain_endpoint,
                  description='The domain-specific endpoint that is used to submit index, search, and data upload '
                              'requests to an Amazon ES domain',
                  export_name=f"{stage_name}-DomainName")
