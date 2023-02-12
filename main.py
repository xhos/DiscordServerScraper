import os
import csv
import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
intents = discord.Intents().all()
client = discord.Client(intents = intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    # Get the channel where you want to save the messages
    channel = client.get_channel(1071827338788094002)

    # Get all messages in the channel
    messages = await channel.history(limit=10).flatten()

    # Create a csv file and write all messages to it
    with open('messages.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Author', 'Message'])
        for message in messages:
            writer.writerow([message.author, message.content])

client.run(token)