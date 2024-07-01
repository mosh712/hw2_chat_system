mkdir packages
pip install -r app/requirements.txt -t packages/

cd terraform
terraform init
terraform apply 
