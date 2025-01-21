# llms

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

brew install ollama
ollama serve > /dev/null 2>&1 &
ollama run smollm2
ollama run smollm2:360m
ollama run smollm2:135m
ollama run llama3.2
ollama run llama3.2:1b
ollama run qwen2.5:3b
ollama run qwen2.5:1.5b
ollama run qwen2.5:0.5b
ollama run hermes3:3b
ollama run phi3.5
ollama run gemma2:2b
ollama run internlm2:1.8b
ollama run deepseek-r1:1.5b

brew install mactop
sudo mactop
```
