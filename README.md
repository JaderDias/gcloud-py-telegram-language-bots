# gcloud-py-telegram-language-bots
Run a telegram bot serverlessly on Google Cloud

## deployment instructions

1. Create one Telegram bot per language with [@BotFather](https://t.me/botfather)

2. Ensure you have an active billing account using [Google Cloud Console](https://console.cloud.google.com/billing)

This project was designed to run for free, since it's not scheduled to execute more often than the free tier of the used services allow. But you're going to need to link it to an active billing account anyway.

3. Clone [this project](https://github.com/JaderDias/gcloud-py-telegram-language-bots) into [Google Cloud Shell](https://shell.cloud.google.com/)

```bash
git clone https://github.com/JaderDias/gcloud-py-telegram-language-bots.git
```

4. Add, modify, and/or remove languages on both `resume-setup.sh` and `terraform/main.tf`

5. Execute the `setup.sh` script