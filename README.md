# Bsuir RAG Assistant Data Loader
A repository of the data loader for Bsuir RAG Assistant

## Endpoints

### ```/health```
Basic health check that returns ```200 OK``` if service is running

#### ```/process_markdown```
This endpoint processes markdown texts with urls and puts them into the Qdrant storage
* __Request .json structure:__
```json
 {
  "source_url": <source_url>,
  "content": <content>
 }
```
* __Response .json structure:__
```json
  {
    "status": <status>,
    "chunks": <number_of_saved_chunks>,
    "embeddings": <number_of_saved_embeddings>
  }
```

## Local running
```docker compose up --build``` and run example.py

### __!!!Warning!!!__
__This service highly depends on:__
  * [bsuir-helper-embedder](https://github.com/semantic-hallucinations/bsuir-helper-embedder) service
  * Qdrant image

_You can view the important ```.env``` variables in ```.env.example```_

## Using docker image
```
services:
  data-loader:
    image: ghcr.io/semantic-hallucinations/bsuir-helper-data-loader:latest   # or commit sha, or tag name instead of <latest>
```
