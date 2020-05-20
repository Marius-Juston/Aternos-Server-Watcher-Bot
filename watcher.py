import asyncio
import os
from urllib.request import urlopen

import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

client = discord.Client()


def get_player_number(soup):
    player_info = soup.find("span", {"class": "info-label"}).text
    num, max_num = map(int, player_info.split('/'))

    return num, max_num


def get_status(soup):
    return soup.find("div", {"class": "status"}).span.text


async def server_status(channel_id):
    await client.wait_until_ready()
    channel: discord.TextChannel = client.get_channel(channel_id)

    if channel is None:
        raise ValueError("The channel could not be found, check the channel id: ", CHANNEL_ID)

    server_ip = os.getenv("SERVER_IP")
    url = f'https://{server_ip}/'

    previous_status = 'Offline'
    current_number_of_players = -1

    while not client.is_closed():
        with urlopen(url) as response:
            html_doc = response.read()
            parser = BeautifulSoup(html_doc, 'html.parser')
            status = get_status(parser)

            if status != previous_status:
                await channel.send(f"The server is now **{status}**")
                previous_status = status

            if status == 'Online':
                num, max_num = get_player_number(parser)

                if num != current_number_of_players:
                    await channel.send(f"There are currently **{num}** players online")

                    current_number_of_players = num

            else:
                current_number_of_players = -1

        await asyncio.sleep(60)  # task runs every 60 seconds


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


client.loop.create_task(server_status(CHANNEL_ID))
client.run(TOKEN)
