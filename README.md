# llms

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

brew install ollama
ollama serve > /dev/null 2>&1 &
ollama pull smollm2
ollama pull smollm2:360m
ollama pull smollm2:135m
ollama pull llama3.2
ollama pull llama3.2:1b
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:0.5b
ollama pull hermes3:3b
ollama pull phi3.5
ollama pull gemma2:2b
ollama pull internlm2:1.8b
ollama pull deepseek-r1:1.5b

brew install mactop
sudo mactop
```
