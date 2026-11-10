def handler(event, context):
    return {
        "statusCode": 200,
        "body": '{"status": "ok", "message": "Financial Advisor Bot is running"}',
        "headers": {"Content-Type": "application/json"}
    }
