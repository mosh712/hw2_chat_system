provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "users" {
  name           = "users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "messages" {
  name           = "messages"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "message_id"

  attribute {
    name = "message_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "chat_metadata" {
  name           = "chat_metadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "chat_id"

  attribute {
    name = "chat_id"
    type = "S"
  }
}

resource "aws_s3_bucket" "cold_storage" {
  bucket = "messaging-system-cold-storage"
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "messaging-system-cache"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis3.2"
}

resource "aws_elasticache_subnet_group" "cache" {
  name       = "cache-subnet-group"
  subnet_ids = ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"]
}
