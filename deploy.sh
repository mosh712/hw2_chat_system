mkdir packages
mkdir packages/python
pip install -r app/requirements.txt -t packages/python

cd terraform
terraform init 
terraform apply -auto-approve
