from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda,
    aws_rds as rds
)

from aws_cdk.core import Construct, Stack


class DbTriggersStack(Stack):

    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str,
                 instance_ref: rds.IDatabaseInstance, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Assign a execution role to the Lambda functions
        base = f'{project_code}-{stage_name}-triggers'
        rds_access_role = iam.Role(self, 'RdsAccessRole',
                                   role_name=f'{base}-{self.region}-lambdaRole',
                                   assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))

        rds_access_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[instance_ref.instance_arn],
            actions=['rds:DescribeDBInstances',
                     'rds:StopDBInstance',
                     'rds:StartDBInstance']
        ))

        # Addition of Lambda job to start the instance
        start_db_function = aws_lambda.Function(self, "StartInstanceFunction",
                                                function_name=f'{project_code}-{stage_name}-start-db-instance',
                                                runtime=aws_lambda.Runtime.PYTHON_3_8,
                                                handler='start_db_instance.handler',
                                                code=aws_lambda.Code.asset('./lambda/start'),
                                                role=rds_access_role,
                                                environment={
                                                    'DB_INSTANCE_NAME': instance_ref.instance_identifier
                                                })

        # Set the job to run every day at 8:30AM UTC
        rule = events.Rule(self, "StartDbRule",
                           rule_name=f'{project_code}-{stage_name}-schedule_db_start',
                           description='Starts the database instance at 8:30 Monday to Friday',
                           enabled=True,
                           schedule=events.Schedule.cron(
                               minute='30',
                               hour='10',
                               month='*',
                               week_day='MON-FRI',
                               year='*'))

        rule.add_target(targets.LambdaFunction(start_db_function))

        # Addition of Lambda job to stop the instance
        stop_db_function = aws_lambda.Function(self, "StopInstanceFunction",
                                               function_name=f'{project_code}-{stage_name}-stop-db-instance',
                                               runtime=aws_lambda.Runtime.PYTHON_3_8,
                                               handler='stop_db_instance.handler',
                                               code=aws_lambda.Code.asset('./lambda/stop'),
                                               role=rds_access_role,
                                               environment={
                                                   'DB_INSTANCE_NAME': instance_ref.instance_identifier
                                               })

        # Set the job to run every day at 4:30PM UTC
        rule = events.Rule(self, "StopDbRule",
                           rule_name=f'{project_code}-{stage_name}-schedule_db_stop',
                           description='Stops the database instance at 4:30 Monday to Friday',
                           enabled=True,
                           schedule=events.Schedule.cron(
                               minute='30',
                               hour='20',
                               month='*',
                               week_day='MON-FRI',
                               year='*'))

        rule.add_target(targets.LambdaFunction(stop_db_function))
