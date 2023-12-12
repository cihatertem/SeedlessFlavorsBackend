#!/bin/bash
docker-compose -f docker-compose-test.yml up --abort-on-container-exit --build;
docker-compose -f docker-compose-test.yml down -v
