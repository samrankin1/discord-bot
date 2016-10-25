import discord
import re

from handlers import Handlers

CLIENT_TOKEN_FILE = "./client_token.txt"
ADMINS_FILE = "./admins.txt"

IMGUR_GIF_REGEX = re.compile("^http://i\.imgur\.com/\w+\.gif$")
IMGUR_MP4_REGEX = re.compile("^http://i\.imgur\.com/\w+\.mp4$")

client = discord.Client()
handlers = None

async def handle_server_message(message):
	print("[SM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)

	if IMGUR_GIF_REGEX.match(message.content) is not None:
		print("[SM] found misformatted imgur gif link ('" + message.content + "'), reformatting to gifv")
		await handlers.handle_imgur_gif_link(message)

	if IMGUR_MP4_REGEX.match(message.content) is not None:
		print("[SM] found misformatted imgur mp4 link ('" + message.content + "'), reformatting to gifv")
		await handlers.handle_imgur_mp4_link(message)

async def handle_group_message(message):
	print("[GM] ignored group message")

async def handle_private_message(message):
	print("[DM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)

	if message.content.lower() == "invite":
		print("[DM] received invite request from @" + str(message.author))
		await handlers.handle_invite_request(message)
		print("[DM] sent invite url to @" + str(message.author))

	if message.content.lower() == "shutdown":
		print("[DM] received shutdown request from @" + str(message.author))
		success = await handlers.handle_shutdown_request(message)
		if success:
			print("[DM] shut down at request of admin @" + str(message.author))
		else:
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

@client.event
async def on_server_join(server):
	print("[global] added to new server: '" + server.name + "'")

@client.event
async def on_server_remove(server):
	print("[global] removed from server: '" + server.name + "'")

def main():
	client_token = None
	with open(CLIENT_TOKEN_FILE, "r") as file:
		client_token = file.readline().strip()

	admins = []
	with open(ADMINS_FILE, "r") as file:
		for line in file.readlines():
			admins.append(line.strip())
	print("loaded " + str(len(admins)) + " administrator(s)")
	print()

	global handlers
	handlers = Handlers(client, admins)

	print("logging in...")
	client.run(client_token)

main()
