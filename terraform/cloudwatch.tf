resource "aws_cloudwatch_event_rule" "every_week" {
  name = "every-week"
  description = "Sends a trigger every week"
  schedule_expression = "cron(0 0 * * 5)"
}

resource "aws_cloudwatch_event_target" "trigger_cmo_strategy" {
  rule = "${aws_cloudwatch_event_rule.every_week.name}"
  target_id = "spotify_analysis"
  arn = "${aws_lambda_function.spotify_analysis.arn}"
}