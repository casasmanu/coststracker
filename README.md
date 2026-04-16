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
- Query last month expenses with `/lastmonth`
- Analyze spending by category with `/analysis`
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
