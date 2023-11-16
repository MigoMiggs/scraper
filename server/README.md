# Server
This is a FastAPI server that serves responses from the LLM plus the specified vector store.

## Setup

Create .env file, with the following:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com<br>
LANGCHAIN_API_KEY=<br>
LANGCHAIN_PROJECT=<br>
OPENAI_API_AZURE_BASE=<br>
OPENAI_API_AZURE_KEY=<br>
OPENAI_API_AZURE_ENGINE=<br>
OPENAI_API_AZURE_VERSION=
```