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

  attribute {
    name = "sender_id"
    type = "S"
  }

  global_secondary_index {
    name            = "sender_id-index"
    hash_key        = "sender_id"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
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

resource "aws_dynamodb_table" "group_members" {
  name           = "group_members"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "group_id"
  range_key      = "user_id"

  attribute {
    name = "group_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "groups" {
  name           = "groups"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "group_id"

  attribute {
    name = "group_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "blocks" {
  name           = "blocks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "block_id"

  attribute {
    name = "block_id"
    type = "S"
  }
}

resource "aws_s3_bucket" "cold_storage" {
  bucket = "messaging-system-cold-storage"
}

# Create VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "main_vpc"
  }
}

# Create Subnets
resource "aws_subnet" "subnet_a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "subnet_a"
  }
}

resource "aws_subnet" "subnet_b" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "subnet_b"
  }
}

# Security Group for Redis ElastiCache
resource "aws_security_group" "redis_sg" {
  name_prefix = "redis-sg-"
  description = "Security group for Redis ElastiCache cluster"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Redis ElastiCache Cluster
resource "aws_elasticache_subnet_group" "cache" {
  name       = "cache-subnet-group"
  subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "messaging-system-cache"
  engine               = "redis"
  engine_version       = "7.0"  # Ensure to match the correct parameter group family
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"  # Correct parameter group family
  subnet_group_name    = aws_elasticache_subnet_group.cache.name
  security_group_ids   = [aws_security_group.redis_sg.id]

  depends_on = [aws_elasticache_subnet_group.cache]
}