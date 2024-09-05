## Networking Demo/POC
- EC2 in public subnet with IGW to connect to internet
- RDS instance in private subnet with with traffic from public EC2 allowed through SG
- Can ping RDS through EC2 address to confirm connection
- Docker container deployed onto EC2 listening on port 8080 (http://ec2-35-183-107-119.ca-central-1.compute.amazonaws.com:8080/)