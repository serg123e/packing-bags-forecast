output "mlflow_db_endpoint" {
  value = aws_db_instance.mlflow_db.endpoint
}

output "grafana_db_endpoint" {
  value = aws_db_instance.grafana_db.endpoint
}
