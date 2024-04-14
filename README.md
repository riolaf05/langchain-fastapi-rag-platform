
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

### Setup 

1. Avviare la VM usando il solito template 

2. Lanciare la pipeline per il seup del microservizio

3. Lanciare i terraform per installare bucket, sns topic ed sns subscription (confermati dall'endpoint installato al punto 2)

### References

* [ChatGPT use cases](https://medium.com/mlearning-ai/10-must-try-chatgpt-prompts-that-will-change-the-way-you-study-3c7a96ce751d)

* [Feedback collector](https://blog.streamlit.io/collecting-user-feedback-on-ml-in-streamlit/)
