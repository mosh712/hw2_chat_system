# Cloud Messaging System

This project implements a backend messaging system similar to Telegram or WhatsApp, deployed on AWS. It supports user registration, messaging, blocking, group management, and message retrieval. 

## Features

- **User Registration**
- **Send Messages to Users**
- **Block Users**
- **Create Groups**
- **Add/Remove Users from Groups**
- **Send Messages to Groups**
- **Retrieve Messages**

## Architecture

The system uses the following AWS services:
- **AWS Lambda** for compute
- **DynamoDB** for data storage
- **ElasticCache** for caching
- **S3** for backups

## Endpoints

- `POST /register` - Register a new user
- `POST /send_message` - Send a message to a user
- `POST /block_user` - Block a user from sending messages
- `POST /create_group` - Create a new group
- `POST /add_user_to_group` - Add a user to a group
- `POST /remove_user_from_group` - Remove a user from a group
- `POST /send_message_to_group` - Send a message to a group
- `POST /get_messages` - Retrieve messages for a user

## Deployment

The deployment uses Terraform for infrastructure management. 

Execute the deploy.sh script