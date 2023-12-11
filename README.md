# Audio Manager
Store small reusable audio and concatendate them on-demand.

# Prerequisites
On your system you should have:
- ffmpeg
- Python

# Installation
```sh
pip install -r requirements.txt
```

# Usage
You should put audio files into the `./res` directory in order for them to be
recognized by Audio Manager.

## GUI
```sh
python controller.py
```

## CLI
```sh
python cli.py
```

## Telegram Bot
Put your Telegram Bot API Token into `TGTOKEN` environment variable, then
```sh
python bot.py
```