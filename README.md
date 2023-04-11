# ProBotX

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9.6](https://img.shields.io/badge/python-3.9.6-blue)](https://www.python.org/downloads/release/python-396/)

**ProBotx** is a feature-rich moderation bot for Discord, built using the [enhanced-dpy](https://github.com/iDutchy/discord.py) library.

---

## Showcase

- I have a showcase server for the bots I make: <a href="https://discord.gg/vS5D4qWDAP"><img src="https://img.shields.io/badge/Discord-7289DA?logo=discord&logoColor=white"></a>
- you could also check the screenshots folder for more.

![Discord_tY0hxFfH1q](https://user-images.githubusercontent.com/52796958/231291622-e8329b7f-fb3c-4e36-9427-cd588f723785.gif)

---

## Features

- **Automatic** messages to members on join/exit, along with designated role assignment.
- **Informative** server and user info embeds.
- **Comprehensive** logging features for member and message updates, including avatar changes, nickname and username changes, and message edits/deletes.
- **A wide range** of mod commands, such as banning, kicking, muting, unmuting, and adding or removing roles, as well as messaging members, purging messages, and sending messages to other channels.
- **ModMail** functionality for seamless communication between moderators and server members.
- **Anonymous Confession** capability, allowing users to share anonymously with mods able to block specific confession IDs.
- **Mod-related logs** for kicks, bans, DMs, and more.
- **Informative error messages** for various command errors.
- **Numerous embeds** with pagination for logs, the help command and other messages for ease of reading.
- **Fun commands** such as fetching wallpapers from Unsplash, checking the weather, rolling dice, polls, and Kanye quotes.

---

## How It's Made

- Python with enhanced-dpy library for Discord bot development.
- To store data related to warned and muted users, I utilized MongoDB as my database management system. This allows store large amounts of data while ensuring optimal performance and scalability.
- To protect user anonymity, I hashed user IDs before they were stored in the database along with their confession messages links so that users that abuse this functionality get banned from using it.
- In order to enhance the functionality of the bot, I integrated a couple of APIs such as:
  - Unsplash for fetching random images
  - OpenWeatherMap for displaying weather information within the server
  - and Kanye West Quotes API for generating random quotes for the server.
- The bot is deployed on Heroku using a CI/CD pipeline for automatic deployment on every push to the main branch.

---

## Lessons Learned

- Learned how to use the enhanced-dpy library for Discord bot development.
- Gained experience in integrating APIs such as Unsplash, OpenWeatherMap, and Kanye West Quotes API into a bot.
- Learned how to utilize MongoDB as a database management system to store warned and muted user data.
- Learned how to hash user IDs for user anonymity when storing them in the database.
- Enhanced my understanding of Python programming and its libraries.
- Developed my problem-solving skills while debugging and testing the bot's functionality.
- Recognized the importance of creating informative error messages for various command errors.
- Gained experience in deploying the bot to Heroku using a CI/CD pipeline for automatic deployment on every push to the main branch.

---

## Installation

To install ProBotx, follow these steps:

1. Visit the [discord developer portal](https://discord.com/developers/applications) and add a bot there (give it admin privileges).
2. Clone the repository.
3. Install `gcc` using `sudo apt install gcc -y`
4. Install dependencies using `pip install -r requirements.txt`
5. copy `env.template` to `.env` and fill the options (bot token, unsplash token, mongodb credentials, etc...)
6. Run the bot using `python pro_bot_x.py`.
