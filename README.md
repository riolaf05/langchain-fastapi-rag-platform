
## Setup
### Setup docker (Ubuntu 22.04) see https://docs.docker.com/engine/install/ubuntu/

```console
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

### Git clone 
```console
git config --global credential.helper store
git clone https://github.com/riolaf05/chatgpt-summmary
sudo docker login
```

### Create certificates
```console
cd certs
mkcert llm.rioengineers.com "*.rioengineers.com" localhost 127.0.0.1 ::1
```

### Setup with Docker

1. Copiare a man .env e config

2. Run

```console
sudo docker run --name riassume -it -d -p 80:8501 -v ./config.yaml:/app/config.yaml -e OPENAI_API_KEY=<env> -e AWS_ACCESS_KEY_ID=<env> -e AWS_SECRET_ACCESS_KEY=<env> -e AWS_REGION=us-east-1 --restart unless-stopped rio05docker/chatgpt-summary:0.0.10
```

### References

* [ChatGPT use cases](https://medium.com/mlearning-ai/10-must-try-chatgpt-prompts-that-will-change-the-way-you-study-3c7a96ce751d)

* [Feedback collector](https://blog.streamlit.io/collecting-user-feedback-on-ml-in-streamlit/)
