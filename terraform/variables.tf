variable "aws_region" {
  description = "The AWS region to deploy in"
  default     = "us-west-2"
}

variable "db_instance_class" {
  description = "The instance class to use for the RDS instance"
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "The allocated storage in gigabytes"
  default     = 20
}

variable "db_engine_version" {
  description = "The version of the database engine to use"
  default     = "12.5"
}

variable "mlflow_db_username" {
  description = "The username for the MLFlow database"
  default     = "mlflowadmin"
}

variable "mlflow_db_password" {
  description = "The password for the MLFlow database"
  default     = "mlflowpassword"
}

variable "grafana_db_username" {
  description = "The username for the Grafana database"
  default     = "grafanaadmin"
}

variable "grafana_db_password" {
  description = "The password for the Grafana database"
  default     = "grafanapassword"
}
