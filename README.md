# Spotlight API

## Docker
To build the container, run the command `docker build -t spotlight-api:latest .`

To run the container after it is built, use the command `docker run -d -p 5000:5000 spotlight-api:latest`

Use `docker ps` to see which containers are currently running. You should see the 
API container running on port 5000 if everything works correctly.

You may also use docker compose to run the service with the command `docker-compose up`.