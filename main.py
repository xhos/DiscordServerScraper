import os
import csv
import yaml
import discord
from dotenv import load_dotenv
from alive_progress import alive_bar


load_dotenv()
token = os.getenv('TOKEN')

with open('config.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

guild_ids = data.get('server_ids', [])
channel_ids = data.get('channel_ids', [])

intents = discord.Intents().all()
client = discord.Client(intents = intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Converts the guild ID's into guild objects
    guilds = []
    if guild_ids:
        for guild_id in guild_ids:
            guild = client.get_guild(guild_id)
            if guild:
                guilds.append(guild)
            else:
                print(f"Couldn't find a guild with ID {guild_id}")

    # If server IDs are specified in config, add all text channels to channel_ids
    if guild_ids:
        for guild in guilds:
            for channel in guild.text_channels:
                if channel.id not in channel_ids:
                    channel_ids.append(channel.id)

    # Converts the channel ID's into channel objects
    channels = []
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel:
            channels.append(channel)
        else:
            print(f"Couldn't find a channel with ID {channel_id}")


    # If no channels are specified, exit with error message
    if not channel_ids:
        print("You haven't entered any ids in config.yaml")
        os._exit(1)

    # Loop through each channel and save the messages
    with alive_bar(len(channel_ids), title='Channels', bar='filling') as channel_bar:
        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            if not channel:
                print(f"Couldn't find a channel with ID {channel_id}")
                continue

            # Get all messages in the channel
            messages = [message async for message in channel.history(limit=None)]
            messages = list(reversed(messages))

            # Write messages to CSV file
            with open(f'{channel.name}.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Index', 'Timestamp', 'Author', 'Author ID', 'Message', 'Has attachment'])
                for i, message in enumerate(messages, start=1):
                    if message.author.bot: # Skip messages sent by bots
                        continue

                    if message.attachments:
                        msgtype = 'attachment'
                        for attachment in message.attachments:
                            writer.writerow([i, message.created_at, message.author, message.author.id, attachment.url, msgtype])
                            i += 1

                    else:
                        if message.content == None or not message.content.strip(): # Skip empty messages
                            continue
                        msgtype = 'regular'
                        message_content = message.content.replace('\n', ' ')
                        writer.writerow([i, message.created_at, message.author, message.author.id, message_content, msgtype])
                        i += 1

            channel_bar()

    print('Scraping complete')
    os._exit(1)

client.run(token)