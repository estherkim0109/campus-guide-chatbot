# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Campus guide chatbot: a serverless RAG Q&A service on AWS (Seoul region, `ap-northeast-2`) that answers student questions from university documents. It's a cloud architecture course project. Code comments and user-facing strings are in Korean.

The project is at an early stage. Only a health-check Lambda and one IAM policy exist so far. There is no build system, dependency manifest, test suite, linter or IaC tool yet. Resources are provisioned by hand in the AWS console, and Lambda code is deployed as zip uploads (`*.zip` is gitignored).

## Target architecture (`docs/architecture.png`)

The diagram is the source of truth for planned components. New code should fit into one of these flows:

- **Query path:** Student → WAF → CloudFront (serves the static frontend from an S3 bucket) → API Gateway `/chat` (Cognito token validation) → Q&A Lambda. That Lambda retrieves from Bedrock Knowledge Bases, generates an answer with Bedrock Claude, and stores conversation history and feedback in DynamoDB.
- **Ingestion path:** An admin uploads documents to the S3 docs bucket (`raw/` and `meta/` prefixes). This triggers EventBridge, then a trigger Lambda, then a Knowledge Base ingestion job. The job chunks and embeds documents with Titan Embeddings V2 and indexes them in OpenSearch Serverless.
- **Cross-cutting:** least-privilege IAM roles per function, KMS encryption, CloudWatch Logs/dashboards/alarms and CloudTrail.

## Layout and conventions

- `backend/<function>/lambda_function.py`: one directory per Lambda, with handler `lambda_handler`. `backend/health/` lists `raw/` in the docs bucket to verify S3 access. Its bucket name comes from the `DOCS_BUCKET` env var.
- `infra/`: IAM policy JSON documents attached to Lambda roles by hand. `campus-guide-docs-read.json` grants read-only access to the `campus-guide-docs-esther` bucket. Keep policies scoped to specific resources.
- `frontend/`: placeholder for the static web app (S3 + CloudFront).
- Lambdas log structured JSON to stdout (`print(json.dumps({"event": ..., ...}, ensure_ascii=False))`) for CloudWatch, and return API Gateway proxy responses with `Content-Type: application/json; charset=utf-8`. Keep `ensure_ascii=False` so Korean text stays readable.

## Running locally

There is no test harness. To exercise a handler, set the env vars and AWS credentials, then call it directly:

```bash
DOCS_BUCKET=campus-guide-docs-esther AWS_REGION=ap-northeast-2 \
  python -c "import sys; sys.path.insert(0,'backend/health'); from lambda_function import lambda_handler; print(lambda_handler({}, None))"
```
