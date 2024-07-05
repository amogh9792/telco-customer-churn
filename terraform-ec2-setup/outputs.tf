output "instance_id" {
  description = "ID of the created EC2 instance"
  value       = aws_instance.my-ec2-tcc.id
}

output "public_ip" {
  description = "Public IP address of the created EC2 instance"
  value       = aws_instance.my-ec2-tcc.public_ip
}
