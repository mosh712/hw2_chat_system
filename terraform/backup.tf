resource "aws_cloudwatch_event_rule" "backup_schedule" {
  name                = "backup-schedule"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "backup_target" {
  rule = aws_cloudwatch_event_rule.backup_schedule.name
  arn  = aws_lambda_function.backup_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_backup_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.backup_schedule.arn
}
