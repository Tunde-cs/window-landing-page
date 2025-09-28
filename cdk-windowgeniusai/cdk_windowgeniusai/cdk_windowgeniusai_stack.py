from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_iam as iam,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    aws_certificatemanager as acm,  # ✅ correct ACM import
    aws_route53 as route53,          # ✅ NEW Route 53 import
    aws_ecr as ecr, 
    Duration,
    CfnOutput
)
from constructs import Construct

class CdkWindowgeniusaiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # 1️⃣ VPC
        vpc = ec2.Vpc.from_lookup(self, "ImportedVPC", vpc_id="vpc-0737754be6fe963b4")

        # 2️⃣ ECS Cluster
        cluster = ecs.Cluster(self, "WindowGeniusCluster", vpc=vpc)

        # 3️⃣ Get Secret from Secrets Manager (contains multiple key-value pairs)
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "WindowGeniusSecret",
            "windowgeniusai-prod-json"
        )

        # 4️⃣ Task Role with permission to pull secrets and write logs
        task_role = iam.Role(
            self, "WindowGeniusTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # 5️⃣ CloudWatch Logs
        log_group = logs.LogGroup(
            self, "WindowGeniusLogGroup",
            log_group_name="/ecs/windowgeniusai", # ✅ fixed log group name
            removal_policy=RemovalPolicy.DESTROY,  # delete on stack destroy (optional)
            retention=logs.RetentionDays.ONE_MONTH      # keep logs for 30 days
        )

        # 6️⃣ Import your existing RDS instead of creating a new one
        rds_instance = rds.DatabaseInstance.from_database_instance_attributes(
            self, "ImportedDB",
            instance_identifier="windowgeniusdb",  # DB identifier
            instance_endpoint_address="windowgeniusdb.c8lcmie8e520.us-east-1.rds.amazonaws.com",
            port=5432,
            security_groups=[
                ec2.SecurityGroup.from_security_group_id(
                    self, "DBSecurityGroup", "sg-05a0d049d5c2b8bf0"  # ✅ your actual RDS SG
                )
            ],

        )

        # 6️⃣.5 Route53 Hosted Zone + ACM Certificate
        hosted_zone = route53.HostedZone.from_lookup(
            self, "WindowGeniusHostedZone",
            domain_name="windowgeniusai.com"
        )

        certificate = acm.DnsValidatedCertificate(
            self, "WindowGeniusDnsCert",
            domain_name="windowgeniusai.com",
            subject_alternative_names=["www.windowgeniusai.com"],
            hosted_zone=hosted_zone,
            region="us-east-1"  # must match your ALB region
        )

        # 🔹 NEW: reference your ECR repo + read image tag from CDK context
        repo = ecr.Repository.from_repository_name(self, "WindowGeniusRepo", "windowgeniusai")
        
        # 🔒 Require an explicit imageTag from CDK context
        image_tag = self.node.try_get_context("imageTag")
        if not image_tag:
            raise ValueError("Missing context 'imageTag'. Call CDK with: -c imageTag=<tag>")

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
                # ⬇️ swap from_registry(:latest) → from_ecr_repository(repo, tag=image_tag)
                image=ecs.ContainerImage.from_ecr_repository(repo, tag=image_tag),
                container_port=8000,
                environment={
                    "PORT": "8000",
                    "DJANGO_SETTINGS_MODULE": "LPageToAdmin.settings",  # ✅ explicitly set Django settings module
                    "USE_AWS_SECRETS": "true",
                    # ✅ Add ALB DNS + custom domain
                    "DJANGO_ALLOWED_HOSTS": "cdkwin-windo-ymgri9fugqm2-695473983.us-east-1.elb.amazonaws.com,www.windowgeniusai.com,windowgeniusai.com",
                },
                secrets={
                    # "DATABASE_URL": ecs.Secret.from_secrets_manager(secret, "DATABASE_URL"),
                    "DATABASE_NAME": ecs.Secret.from_secrets_manager(secret, "DATABASE_NAME"),
                    "DATABASE_USER": ecs.Secret.from_secrets_manager(secret, "DATABASE_USER"),
                    "DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(secret, "DATABASE_PASSWORD"),
                    "DATABASE_HOST": ecs.Secret.from_secrets_manager(secret, "DATABASE_HOST"),
                    "DATABASE_PORT": ecs.Secret.from_secrets_manager(secret, "DATABASE_PORT"),
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
            ),
            # 👇 this goes OUTSIDE the `task_image_options`
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),  # auto rollback on failed deploys
            certificate=certificate,  # 👈 use the Route53-validated cert you created above
            redirect_http=True  # force all traffic to HTTPS

        )
        # 🔐 Allow ECS tasks to connect to RDS on port 5432
        rds_instance.connections.allow_default_port_from(
        service.service, "Allow ECS tasks to access Postgres"
        )

        
        # ✅ Allow ECS to inject the secrets from Secrets Manager
        exec_role = service.task_definition.obtain_execution_role()
        secret.grant_read(exec_role)

        # ✅ Give ECS permission to pull from ECR
        exec_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        # ✅ Also allow the Task Role to read secrets
        secret.grant_read(task_role)

        # ✅ Required for ECS Exec (SSM) – minimal inline policy
        for role in [exec_role, task_role]:
            role.add_to_policy(iam.PolicyStatement(
                actions=[
                    "ssmmessages:CreateControlChannel",
                    "ssmmessages:CreateDataChannel",
                    "ssmmessages:OpenControlChannel",
                    "ssmmessages:OpenDataChannel",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            ))


        # Configure Health Check on the ALB Target Group
        service.target_group.configure_health_check(
            path="/health/",
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_http_codes="200",
        )
        # Extra ECS configs
        service.service.enable_execute_command = True
        service.service.health_check_grace_period = Duration.seconds(600)  # ⬅️ 10 minutes


        # 7️⃣ Output Load Balancer DNS
        CfnOutput(
            self, "LoadBalancerDNS",
            value=service.load_balancer.load_balancer_dns_name,
            description="Public URL of the deployed WindowGeniusAI app",
            export_name="WindowGeniusALB"
        )

        