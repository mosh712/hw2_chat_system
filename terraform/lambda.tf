data "archive_file" "my_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../packages/"
  output_path = "${path.module}/../lambda_modules_layer.zip"
}

resource "aws_lambda_layer_version" "my_layer" {
  filename   = data.archive_file.my_layer.output_path
  layer_name = "my-layer"
  compatible_runtimes = ["python3.9"]

  source_code_hash = data.archive_file.my_layer.output_base64sha256
}

# IAM Role and Policy for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:*",
          "s3:*",
          "logs:*"
        ],
        Resource = "*"
      }
    ]
  })
}

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

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
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
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  layers = [
    aws_lambda_layer_version.my_layer.arn
  ]
  environment {
    variables = {
      S3_BUCKET_NAME          = aws_s3_bucket.cold_storage.bucket
      REDIS_HOST              = aws_elasticache_cluster.redis.cache_nodes[0].address
      REDIS_PORT              = aws_elasticache_cluster.redis.port
      DYNAMODB_ENDPOINT_URL   = "https://dynamodb.${var.aws_region}.amazonaws.com"
      S3_ENDPOINT_URL         = "https://s3.${var.aws_region}.amazonaws.com"
      CACHE_LAST_X_MESSAGES   = "10"
      DB_LAST_Y_MESSAGES      = "50"
      S3_RETENTION_DAYS       = "365"
      DB_LIMIT                = "1000"
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
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  layers = [
    aws_lambda_layer_version.my_layer.arn
  ]
  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.cold_storage.bucket
      DB_RETENTION_HOURS  = "24"
      S3_RETENTION_DAYS   = "365"
    }
  }
}
