from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_iam as iam,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    Duration,
    CfnOutput
)
from constructs import Construct

class CdkWindowgeniusaiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # 1️⃣ VPC
        vpc = ec2.Vpc(self, "WindowGeniusVPC", max_azs=2)

        # 2️⃣ ECS Cluster
        cluster = ecs.Cluster(self, "WindowGeniusCluster", vpc=vpc)

        # Create RDS credentials
        db_credentials = rds.Credentials.from_generated_secret("dbmaster")  # ✅ NOT a reserved word

        # 3️⃣ Get Secret from Secrets Manager (contains multiple key-value pairs)
        secret = secretsmanager.Secret.from_secret_complete_arn(
            self, "WindowGeniusSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-1:629965575535:secret:windowgeniusai-prod-zJRocM"
        )

        # 4️⃣ Task Role with permission to pull secrets and write logs
        task_role = iam.Role(
            self, "WindowGeniusTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
            ]
        )

        # 5️⃣ CloudWatch Logs
        log_group = logs.LogGroup(self, "WindowGeniusLogGroup")

        # Create the RDS instance
        rds_instance = rds.DatabaseInstance(
            self, "WindowGeniusDB",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            database_name="windowgeniusdb",
            credentials=db_credentials,
            publicly_accessible=False,  # or False for tighter security
            deletion_protection=False,
            
        )

        # 6️⃣ Fargate Service with Load Balancer
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WindowGeniusService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            public_load_balancer=True,
            assign_public_ip=True,
            desired_count=1,
            task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            platform_version=ecs.FargatePlatformVersion.LATEST,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                container_name="windowgeniusai",
                image=ecs.ContainerImage.from_registry(
                    "629965575535.dkr.ecr.us-east-1.amazonaws.com/windowgeniusai:latest"
                ),
                container_port=8000,
                environment={
                    "PORT": "8000"
                },
                secrets={
                    "DATABASE_URL": ecs.Secret.from_secrets_manager(secret, "DATABASE_URL"),
                    "DATABASE_NAME": ecs.Secret.from_secrets_manager(secret, "dbname"),
                    "DATABASE_USER": ecs.Secret.from_secrets_manager(secret, "username"),
                    "DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(secret, "password"),
                    "DATABASE_HOST": ecs.Secret.from_secrets_manager(secret, "host"),
                    "DATABASE_PORT": ecs.Secret.from_secrets_manager(secret, "port"),
                    "SECRET_KEY": ecs.Secret.from_secrets_manager(secret, "SECRET_KEY"),
                    "DEBUG": ecs.Secret.from_secrets_manager(secret, "DEBUG"),
                    "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(secret, "OPENAI_API_KEY"),
                    "EMAIL_HOST_USER": ecs.Secret.from_secrets_manager(secret, "EMAIL_HOST_USER"),
                    "EMAIL_HOST_PASSWORD": ecs.Secret.from_secrets_manager(secret, "EMAIL_HOST_PASSWORD"),
                    "DEFAULT_FROM_EMAIL": ecs.Secret.from_secrets_manager(secret, "DEFAULT_FROM_EMAIL"),
                    "SALES_EMAIL": ecs.Secret.from_secrets_manager(secret, "SALES_EMAIL"),
                    "CLOUDINARY_CLOUD_NAME": ecs.Secret.from_secrets_manager(secret, "CLOUDINARY_CLOUD_NAME"),
                    "CLOUDINARY_API_KEY": ecs.Secret.from_secrets_manager(secret, "CLOUDINARY_API_KEY"),
                    "CLOUDINARY_API_SECRET": ecs.Secret.from_secrets_manager(secret, "CLOUDINARY_API_SECRET"),
                    "FB_PAGE_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(secret, "FB_PAGE_ACCESS_TOKEN")
                },
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="windowgeniusai",
                    log_group=log_group
                ),
                task_role=task_role
            )
        )
        # Configure Health Check on the ALB Target Group
        service.target_group.configure_health_check(
            path="/health/",
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
        )


        # 7️⃣ Output Load Balancer DNS
        CfnOutput(
            self, "LoadBalancerDNS",
            value=service.load_balancer.load_balancer_dns_name,
            description="Public URL of the deployed WindowGeniusAI app",
            export_name="WindowGeniusALB"
        )

        
        
