# Window Genius AI – Smart Window Lead Generation Platform

![AWS](https://img.shields.io/badge/AWS-ECS%20Fargate-orange?logo=amazon-aws&logoColor=white)
![CI/CD](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions&logoColor=white)
![Deployed to AWS](https://img.shields.io/badge/Deployed-AWS--ECS--Fargate-green?logo=amazonaws)
![Status: Live](https://img.shields.io/badge/Status-Live-brightgreen)

![Landing Screenshot](static/assets/img/landing-screenshot.png)


**Window Genius AI** is a full-stack Django CRM and lead generation system designed for window installation businesses in the U.S. Built and deployed by a **Software Engineer** and **Cloud DevOps Engineer**, it combines modern web development with production-ready AWS infrastructure.

---

## 🚀 Features

- ✨ High-converting landing page (Bootstrap 5) optimized for SEO & conversions  
- 💬 AI-powered chatbot (OpenAI GPT-3.5) that captures and qualifies leads interactively  
- 📩 Smart quote request form with **real-time email + dashboard notifications**  
- 📊 Custom AdminLTE dashboard:  
  - Lead tracking & centralized inbox  
  - Quote lifecycle management (New → Pending → Active → Completed)  
  - Order tracking, revenue metrics & reporting  
- 🔗 Facebook Lead Ads integration via Webhooks  
  (Permissions: `leads_retrieval`, `pages_read_engagement`, `pages_show_list`)  
- 🧠 SaaS-ready onboarding with pricing plans (Starter, Pro, Agency)  
  - Stripe subscription payments, Calendly scheduling, Google Forms intake  
- 🔐 Secure user authentication with role-based access & session management  
- ☁️ **Cloud-native deployment**:  
  - AWS ECS Fargate for container orchestration  
  - ALB (Application Load Balancer) with HTTPS via ACM  
  - Auto-rollback deployments with ECS deployment circuit breaker  
- 🧱 Container image stored in **Amazon ECR** & deployed via GitHub Actions CI/CD  
- 🔐 **Secrets management** with AWS Secrets Manager & encrypted S3 environment files  
- 📈 **Monitoring & Observability**:  
  - Centralized logging with CloudWatch Logs  
  - Health checks via ALB → ECS tasks  
  - Metrics and scaling policies ready for production  
- 🛡️ **Security Best Practices**:  
  - Enforced HTTPS with ACM certificates  
  - CSP headers & Django security middleware  
  - `.gitignore` / `.dockerignore` with **Gitleaks scanning** to prevent secret exposure  
- 🔄 **End-to-end CI/CD pipeline**:  
  - Code pushed → GitHub Actions → Docker build → ECR → ECS deploy → health check verified  
- 🧠 **Built following Cloud Platform Engineering & DevOps best practices**

---

## 🧠 Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Backend:** Django, SQLite (dev), PostgreSQL (prod)
- **Chatbot:** OpenAI GPT-3.5
- **CI/CD:** GitHub Actions
- **Cloud:** AWS (ECS Fargate, ECR, S3, Secrets Manager, CloudWatch, ALB)
- **Containerization:** Docker
- **Email:** SMTP via Django
- **Security:** CSP, HTTPS, SEO, GA4, role-based access

---

## ☁️ Deployment Workflow (DevOps/Cloud Platform Engineer Role)

1. **CI/CD Pipeline** (GitHub Actions)  
   - Lints/tests code → builds Docker image → pushes to Amazon ECR → deploys ECS service.  

2. **Infrastructure as Code** (AWS CDK)  
   - ECS Fargate cluster + ALB + target groups.  
   - RDS PostgreSQL (encrypted, private subnets).  
   - S3 for config & static assets.  
   - Secrets Manager for credentials & API keys.  

3. **Observability & Scaling**  
   - CloudWatch logs for container output & metrics.  
   - ALB health checks for rolling deployments.  
   - Auto-rollback with ECS deployment circuit breaker.  
## 📸 Screenshots

---


### ECS Tasks (Fargate)

> Deployment live on AWS ECS Fargate 🚀  
> Includes real-time scaling, health checks, and task logging.  
> Live tasks running on Amazon ECS with health checks and rolling deployments

![ECS Tasks Screenshot](static/assets/img/ecs-tasks.png)

### AWS Load Balancer (ALB)

> Application Load Balancer routing traffic with high availability zones

![ALB Screenshot](static/assets/img/alb-dashboard.png)

### ECS CloudWatch Logs

> Django boot logs captured in AWS CloudWatch for ECS container observability

![CloudWatch Logs](static/assets/img/cloudwatch-logs.png)


---

## ⚙️ Run Locally with Docker

```bash
git clone https://github.com/Tunde-cs/window-landing-page.git
cd window-landing-page
docker build -t windowgeniusai .
docker run -p 8000:8000 windowgeniusai
