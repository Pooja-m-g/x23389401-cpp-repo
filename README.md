         ___        ______     ____ _                 _  ___  
        / \ \      / / ___|   / ___| | ___  _   _  __| |/ _ \ 
       / _ \ \ /\ / /\___ \  | |   | |/ _ \| | | |/ _` | (_) |
      / ___ \ V  V /  ___) | | |___| | (_) | |_| | (_| |\__, |
     /_/   \_\_/\_/  |____/   \____|_|\___/ \__,_|\__,_|  /_/ 
 ----------------------------------------------------------------- 


Hi there! Welcome to AWS Cloud9!

To get started, create some files, play with the terminal,
or visit https://docs.aws.amazon.com/console/cloud9/ for our documentation.

Happy coding!



aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 721294956586.dkr.ecr.us-east-1.amazonaws.com

docker build -t x23389401-ecr:latest .

docker tag x23389401-ecr:latest 721294956586.dkr.ecr.us-east-1.amazonaws.com/x23389401-ecr:latest

docker push 721294956586.dkr.ecr.us-east-1.amazonaws.com/x23389401-ecr:latest