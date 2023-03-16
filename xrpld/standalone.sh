#!/bin/bash

# Start rippled in standalone
docker compose -f docker-compose.yml up --build --force-recreate -d && exec ./rippled --start --conf config/rippled.cfg -a
