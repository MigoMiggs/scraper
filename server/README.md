# Server
This is a FastAPI server that serves responses from the LLM plus the specified vector store.

## Setup

Create .env file, with the following:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com<
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=
OPENAI_API_AZURE_BASE=
OPENAI_API_AZURE_KEY=
OPENAI_API_AZURE_ENGINE=
OPENAI_API_AZURE_VERSION=
```