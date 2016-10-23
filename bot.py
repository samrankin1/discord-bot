import discord
import asyncio
import re

CLIENT_TOKEN_FILE = "./client_token.txt"
ADMINS_FILE = "./admins.txt"

IMGUR_GIF_REGEX = re.compile("^http://i\.imgur\.com/\w+\.gif$")
IMGUR_MP4_REGEX = re.compile("^http://i\.imgur\.com/\w+\.mp4$")

client = discord.Client()

admins = []

def is_admin(user):
	return (user.id in admins)

async def handle_server_message(message):
	print("[SM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)
	
	if IMGUR_GIF_REGEX.match(message.content) is not None:
		print("[SM] found misformatted imgur gif link ('" + message.content + "'), reformatting to gifv")
		updated_link = message.content.replace(".gif", ".gifv")
		await client.send_message(message.channel, "automatically reformatted gif link to gifv" + "\n" + updated_link)
		
	if IMGUR_MP4_REGEX.match(message.content) is not None:
		print("[SM] found misformatted imgur mp4 link ('" + message.content + "'), reformatting to gifv")
		updated_link = message.content.replace(".mp4", ".gifv")
		await client.send_message(message.channel, "automatically reformatted mp4 link to gifv" + "\n" + updated_link)

async def handle_group_message(message):
	print("[GM] ignored group message")

async def handle_private_message(message):
	print("[DM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)

	if message.content.lower() == "invite":
		print("[DM] received invite request from @" + str(message.author))
		invite_url = discord.utils.oauth_url(client.user.id, permissions = discord.Permissions.all())
		await client.send_message(message.channel, invite_url)
		print("[DM] sent invite url to @" + str(message.author))

	if message.content.lower() == "shutdown":
		print("[DM] received shutdown request from @" + str(message.author))
		if is_admin(message.author):
			await client.send_message(message.channel, "shutting down...")
			print("[DM] shutting down at request of admin @" + str(message.author))
			await client.close()
		else:
			await client.send_message(message.channel, "only administrators can shut down the bot!")
			print("[DM] denied shutdown request of non-admin @" + str(message.author))

@client.event
async def on_ready():
	print("successfully logged in as '" + client.user.name + "' (ID: " + client.user.id + ")")
	print("connected to " + str(len(client.servers)) + " server(s)")
	print()

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	await {
	discord.ChannelType.text: handle_server_message,
	discord.ChannelType.group: handle_group_message,
	discord.ChannelType.private: handle_private_message
	}[message.channel.type](message)

def main():
	client_token = None
	with open(CLIENT_TOKEN_FILE, "r") as file:
		client_token = file.readline().strip()

	global admins
	with open(ADMINS_FILE, "r") as file:
		for line in file.readlines():
			admins.append(line)
	print("loaded " + str(len(admins)) + " administrator(s)")
	print()

	print("logging in...")
	client.run(client_token)

main()