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

DE_DICT="de.csv"
ES_DICT="es.csv"
FR_DICT="fr.csv"
IT_DICT="it.csv"
NL_DICT="nl.csv"
PT_DICT="pt.csv"
SH_DICT="sh.csv"
if [ ! -f "$DE_DICT" ] || [ ! -f "$ES_DICT" ] || [ ! -f "$FR_DICT" ] || [ ! -f "$IT_DICT" ] || [ ! -f "$NL_DICT" ] || [ ! -f "$PT_DICT" ] || [ ! -f "$SH_DICT" ]; then
    DUMP_XML_BZ2="enwiktionary-latest-pages-articles-multistream.xml.bz2"
    if [ ! -f "$DUMP_XML_BZ2" ]; then
        wget "https://dumps.wikimedia.org/enwiktionary/latest/$DUMP_XML_BZ2"
    fi
    if [ ! -f "$DE_DICT" ]; then
        python3 filter_wiktionary.py German A-ZÀäüöß $DUMP_XML_BZ2 | tee $DE_DICT
    fi
    if [ ! -f "$ES_DICT" ]; then
        python3 filter_wiktionary.py Spanish A-Záííñóúü $DUMP_XML_BZ2 | tee $ES_DICT
    fi
    if [ ! -f "$FR_DICT" ]; then
        python3 filter_wiktionary.py French A-ZÀÂÆÉÈÙÊÎÔÛËÏÇ $DUMP_XML_BZ2 | tee $FR_DICT
    fi
    if [ ! -f "$IT_DICT" ]; then
        python3 filter_wiktionary.py Italian A-ZÀÂÆÉÈÙÊÎÔÛËÏÇ $DUMP_XML_BZ2 | tee $IT_DICT
    fi
    if [ ! -f "$NL_DICT" ]; then
        python3 filter_wiktionary.py Dutch A-ZÁÉÍÓÚÀÈËÏÖÜĲ $DUMP_XML_BZ2 | tee $NL_DICT
    fi
    if [ ! -f "$PT_DICT" ]; then
        python3 filter_wiktionary.py Portuguese A-Zãáàâçéêíõóôúü $DUMP_XML_BZ2 | tee $PT_DICT
    fi
    if [ ! -f "$SH_DICT" ]; then
        python3 filter_wiktionary.py Serbo-Croatian A-ZÁČĆĐÍĽŇÔŠŤÚÝŽ $DUMP_XML_BZ2 | tee $SH_DICT
    fi
fi

cd terraform

terraform init

DE_TOKEN=`gcloud secrets versions access latest --secret="telegram-de-token"`
if [ -z "$DE_TOKEN" ]
then
    printf "paste the telegram bot token for the DE language: "
    read DE_TOKEN
fi

ES_TOKEN=`gcloud secrets versions access latest --secret="telegram-es-token"`
if [ -z "$ES_TOKEN" ]
then
    printf "paste the telegram bot token for the ES language: "
    read ES_TOKEN
fi

FR_TOKEN=`gcloud secrets versions access latest --secret="telegram-fr-token"`
if [ -z "$FR_TOKEN" ]
then
    printf "paste the telegram bot token for the FR language: "
    read FR_TOKEN
fi

IT_TOKEN=`gcloud secrets versions access latest --secret="telegram-it-token"`
if [ -z "$IT_TOKEN" ]
then
    printf "paste the telegram bot token for the IT language: "
    read IT_TOKEN
fi

NL_TOKEN=`gcloud secrets versions access latest --secret="telegram-nl-token"`
if [ -z "$NL_TOKEN" ]
then
    printf "paste the telegram bot token for the NL language: "
    read NL_TOKEN
fi

PT_TOKEN=`gcloud secrets versions access latest --secret="telegram-pt-token"`
if [ -z "$PT_TOKEN" ]
then
    printf "paste the telegram bot token for the NL language: "
    read PT_TOKEN
fi

SH_TOKEN=`gcloud secrets versions access latest --secret="telegram-sh-token"`
if [ -z "$SH_TOKEN" ]
then
    printf "paste the telegram bot token for the SH language: "
    read SH_TOKEN
fi

terraform apply --var "project=$PROJECT_ID"\
    --var "de_token=$DE_TOKEN"\
    --var "es_token=$ES_TOKEN"\
    --var "fr_token=$FR_TOKEN"\
    --var "it_token=$IT_TOKEN"\
    --var "nl_token=$NL_TOKEN"\
    --var "pt_token=$PT_TOKEN"\
    --var "sh_token=$SH_TOKEN"
