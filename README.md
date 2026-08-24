# coststracker
Project intended to track my income and expenses.

Main idea:
- Create one main Excel file to track income, fixed and variable costs, and savings.
- Have a dedicated sheet for variable costs, for example:
  description | amount | date | comments
- Use a Telegram bot with the following features:
- Infinite polling to receive messages
- Receive amount and description. OPTIONAL: add date, default date is now()
- Add the cost to an Excel sheet
- Keep expenses ordered by date
- OPTIONAL: MySQL database
- Use Docker to deploy everything and keep the code organized, so migration from an RPi keeps working

....

Initial config variables:
- CSV PATH - Excel should be in a specific path, and if it does not exist the code should create it.
- Bot token
-

HOW TO SET UP
To set up the environment, run the following commands:
- python -m venv .venv
- source ./.venv/bin/activate
- pip install -r ./requirements.txt


HOW TO USE DOCKER
Build the image with the name coststracker-bot:
docker build -t coststracker-bot .

Then add the image to docker compose:
version: "3.9"
services:
  bot:
    image: coststracker-bot
    volumes:
      - /home/manu/Workspace/coststracker:/app
      - /mnt:/mnt/
    env_file:
      - .env
    restart: unless-stopped


PUBLISH TO DOCKER HUB WITH VERSION TAGS
This repository includes a GitHub Actions workflow at .github/workflows/docker-publish.yml.

1. Configure repository secrets in GitHub:
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN (Docker Hub access token, not your password)

2. Workflow behavior:
- Push to main: publishes username/coststracker-bot:latest and username/coststracker-bot:sha-<shortsha>
- Push git tag vX.Y.Z: publishes username/coststracker-bot:vX.Y.Z and username/coststracker-bot:X.Y.Z
- Manual run (Actions tab): you can pass version input (example 1.4.0)

3. Example release flow:
- git tag v1.0.0
- git push origin v1.0.0

4. Example docker-compose usage from any server:
version: "3.9"
services:
  bot:
    image: <dockerhub-username>/coststracker-bot:v1.0.0
    env_file:
      - .env
    restart: unless-stopped