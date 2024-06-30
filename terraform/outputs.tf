output "lambda_function_url" {
  value = aws_lambda_function.lambda.invoke_arn
}
