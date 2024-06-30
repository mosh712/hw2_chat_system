resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../app"
  output_path = "${path.module}/../app/lambda_function.zip"
}

resource "aws_lambda_function" "messaging_system_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "messaging_system_lambda"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  environment {
    variables = {
      DYNAMODB_TABLE_USERS    = aws_dynamodb_table.users.name
      DYNAMODB_TABLE_MESSAGES = aws_dynamodb_table.messages.name
      S3_BUCKET_NAME          = aws_s3_bucket.cold_storage.bucket
      REDIS_HOST              = aws_elasticache_cluster.redis.cache_nodes[0].address
      REDIS_PORT              = aws_elasticache_cluster.redis.port
    }
  }
}

resource "aws_lambda_function_url" "lambda_url" {
  function_name = aws_lambda_function.messaging_system_lambda.function_name
  authorization_type = "NONE"
}

output "lambda_function_url" {
  value = aws_lambda_function_url.lambda_url.function_url
}

resource "aws_lambda_function" "backup_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "backup_lambda"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "backup_lambda_function.lambda_handler"
  runtime          = "python3.8"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.cold_storage.bucket
      DB_RETENTION_HOURS  = "24"
      S3_RETENTION_DAYS   = "365"
    }
  }
}
