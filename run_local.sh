#!/bin/bash
docker build -t windowgeniusai .
docker run -d -p 8000:8000 windowgeniusai

