# coststracker
project destinated to follow my incomes and expenses. 

main idea:
- create a main excel, where i can follow my incomes, fix and variables costs and my savings.
- have one different sheet with the variables costs, something like:
    description | cuantity | date | comments
- have a bot in telegram with the next functionalities:
- infinite polling to receive messages
- receive message with cuantity and description. OPTIONAL: add date, by default the date is now()
- add the cost to a excel sheet
- the sheet will order the expenses by date
- OPTIONAL: mysql Database
- use docker to deploy everything and have the code organized, so if i migrate the app from rpi will continue working

....

initial config variables:
- CSV PATH - excel should be in certain path, if not the code should create it.
- bot token
- 

HOW TO Setup
in order to set up the environment, run the next commands:
- python -m venv .venv
- source ./.venv/bin/activate
- pip install -r ./requierements.txt


HOW TO DOCKER
buildear la imagen con el nombre coststracker-bot
docker build -t coststracker-bot .

luego agregar la imagen al docker compose
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