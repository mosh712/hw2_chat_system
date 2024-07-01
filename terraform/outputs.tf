output "lambda_function_name" {
  value = aws_lambda_function.messaging_system_lambda.function_name
}

output "dynamodb_tables" {
  value = [
    aws_dynamodb_table.users.name,
    aws_dynamodb_table.messages.name,
    aws_dynamodb_table.chat_metadata.name,
    aws_dynamodb_table.group_members.name,
    aws_dynamodb_table.groups.name,
    aws_dynamodb_table.blocks.name
  ]
}

output "s3_bucket" {
  value = aws_s3_bucket.cold_storage.bucket
}

output "lambda_function_url_output" {
  value = aws_lambda_function.messaging_system_lambda.invoke_arn
}
