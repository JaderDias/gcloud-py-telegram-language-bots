#!/bin/sh

./set-project.sh

DEV_TOKEN=`gcloud secrets versions access latest --secret="telegram-dev-token"`
if [ -z "$DEV_TOKEN" ]
then
    printf "paste the telegram bot token for the dev enviroment: "
    read DEV_TOKEN
    printf "$DEV_TOKEN" | gcloud secrets create telegram-dev-token --data-file=-
fi

cd python/langbot

python3 main.py