#!/bin/sh

./set-project.sh

PROJECT_ID=$(gcloud config get-value project)

gcloud services enable \
    appengine.googleapis.com \
    cloudbuild.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudscheduler.googleapis.com \
    firestore.googleapis.com \
    pubsub.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com

NL_DICT="nl.csv"
PT_DICT="pt.csv"
SH_DICT="sh.csv"
if [ ! -f "$NL_DICT" ] || [ ! -f "$PT_DICT" ] || [ ! -f "$SH_DICT" ]; then
    DUMP_XML_BZ2="enwiktionary-latest-pages-articles-multistream.xml.bz2"
    if [ ! -f "../$DUMP_XML_BZ2" ]; then
        wget "https://dumps.wikimedia.org/enwiktionary/latest/$DUMP_XML_BZ2"
    fi
    if [ ! -f "$NL_DICT" ]; then
        python3 python/parser/filter_wiktionary.py Dutch A-ZÁÉÍÓÚÀÈËÏÖÜĲ ../$DUMP_XML_BZ2 | tee $NL_DICT
    fi
    if [ ! -f "$PT_DICT" ]; then
        python3 python/parser/filter_wiktionary.py Portuguese A-Zãáàâçéêíõóôúü ../$DUMP_XML_BZ2 | tee $PT_DICT
    fi
    if [ ! -f "$SH_DICT" ]; then
        python3 python/parser/filter_wiktionary.py Serbo-Croatian A-ZÁČĆĐÍĽŇÔŠŤÚÝŽ ../$DUMP_XML_BZ2 | tee $SH_DICT
    fi
fi

cd terraform

terraform init

NL_TOKEN=`gcloud secrets versions access latest --secret="telegram-nl-token"`
if [ -z "$NL_TOKEN" ]
then
    printf "paste the telegram bot token for the NL language: "
    read NL_TOKEN
fi

PT_TOKEN=`gcloud secrets versions access latest --secret="telegram-pt-token"`
if [ -z "$PT_TOKEN" ]
then
    printf "paste the telegram bot token for the PT language: "
    read PT_TOKEN
fi

SH_TOKEN=`gcloud secrets versions access latest --secret="telegram-sh-token"`
if [ -z "$SH_TOKEN" ]
then
    printf "paste the telegram bot token for the SH language: "
    read SH_TOKEN
fi

terraform apply --var "project=$PROJECT_ID"\
    --var "nl_token=$NL_TOKEN"\
    --var "pt_token=$PT_TOKEN"\
    --var "sh_token=$SH_TOKEN"
