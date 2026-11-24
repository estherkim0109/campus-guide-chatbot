import json, os, datetime, boto3

s3 = boto3.client("s3")
BUCKET = os.environ["DOCS_BUCKET"]

def lambda_handler(event, context):
    try:
        res = s3.list_objects_v2(Bucket=BUCKET, Prefix="raw/")
        # 폴더(끝이 /인 키)는 빼고 실제 파일만 셈
        files = [o["Key"] for o in res.get("Contents", []) if not o["Key"].endswith("/")]
        s3_ok = True
    except Exception as e:
        files, s3_ok = [], False
        print(json.dumps({"event": "s3_error", "error": str(e)}))

    body = {
        "service": "campus-guide",
        "status": "ok",
        "s3_access": s3_ok,
        "doc_count": len(files),
        "docs": files[:5],
        "region": os.environ.get("AWS_REGION"),
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    print(json.dumps({"event": "health_check", **body}, ensure_ascii=False))  # CloudWatch 확인용
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }