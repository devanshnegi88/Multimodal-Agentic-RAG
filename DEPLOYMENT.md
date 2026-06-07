# Deployment

This repository includes artifacts to deploy to both Render and AWS ECS (Fargate).

Render
- `render.yaml` in the repo root configures two services:
  - `agentic-rag-backend` — Docker-built from `docker/Dockerfile.backend`.
  - `agentic-rag-frontend` — Static site built from `frontend` and published from `frontend/dist`.

To deploy on Render: push this repo to a Git provider, then connect the repo in the Render dashboard and choose the services defined in `render.yaml` (secrets and environment variables must be configured in the Render dashboard).

AWS (ECS / Fargate)
- A GitHub Actions workflow has been added at `.github/workflows/deploy_aws.yml`.
- The workflow builds and pushes Docker images for the backend and frontend to ECR and registers ECS task definitions using the templates in `deploy/aws/`.

Required GitHub secrets (set in repository Settings > Secrets and variables > Actions):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_ACCOUNT_ID`
- `ECS_CLUSTER` (ECS cluster name)
- `ECS_SERVICE_BACKEND` (ECS service name for backend)
- `ECS_SERVICE_FRONTEND` (ECS service name for frontend)

Notes
- The ECS task definition templates include placeholders for roles (`executionRoleArn` and `taskRoleArn`) and a placeholder `IMAGE_PLACEHOLDER` that the workflow replaces with the built image URI. Update the ARNs with valid roles that allow `ecs` and `logs` operations.
- You may prefer to use App Runner, Elastic Beanstalk, or CloudFormation/Terraform for a more opinionated production setup; these artifacts are a minimally invasive starting point.
