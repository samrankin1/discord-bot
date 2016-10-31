import discord
import re

from handlers import Handlers

CLIENT_TOKEN_FILE = "./client_token.txt"
YOUTUBE_TOKEN_FILE = "./youtube_token.txt"
ADMINS_FILE = "./admins.txt"

IMGUR_GIF_MP4_REGEX = re.compile("^(https?://i\.imgur\.com/\w+)\.(?:gif|mp4)$") # matches a imgur .gif or .mp4 link, capturing the URL minus the extension
SPOTIFY_TRACK_REGEX = re.compile("^(?:spotify:track:|https?://open\.spotify\.com/track/)(\w+)$") # matches a spotify:track:xyz or http://open.spotify.com/track/xyz link, capturing the track ID
INVITE_COMMAND_REGEX = re.compile("^invite$") # matches exactly "invite"
SHUTDOWN_COMMAND_REGEX = re.compile("^shut ?down$") # matches exactly "shutdown" or "shut down"

client = discord.Client()
handlers = None

async def handle_server_message(message):
	print("[SM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)

	imgur_match = IMGUR_GIF_MP4_REGEX.search(message.content)
	if imgur_match:
		print("[SM] found misformatted imgur link ('" + message.content + "'), reformatting to gifv")
		naked_url = imgur_match.group(1)
		await handlers.handle_imgur_gif_mp4_link(naked_url, message)

	spotify_match = SPOTIFY_TRACK_REGEX.search(message.content)
	if spotify_match:
		print("[SM] found spotify track URI ('" + message.content + "'), attempting to find youtube equivalent")
		track_id = spotify_match.group(1)
		await handlers.handle_spotify_track(track_id, message)

async def handle_group_message(message):
	print("[GM] ignored group message")

async def handle_private_message(message):
	print("[DM] from @" + str(message.author) + " [" + message.author.id + "]: " + message.content)

	if INVITE_COMMAND_REGEX.search(message.content):
		print("[DM] received invite request from @" + str(message.author))
		await handlers.handle_invite_request(message)
		print("[DM] sent invite url to @" + str(message.author))

	if SHUTDOWN_COMMAND_REGEX.search(message.content):
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

	youtube_token = None
	with open(YOUTUBE_TOKEN_FILE, "r") as file:
		youtube_token = file.readline().strip()

	admins = []
	with open(ADMINS_FILE, "r") as file:
		for line in file.readlines():
			admins.append(line.strip())
	print("loaded " + str(len(admins)) + " administrator(s)")
	print()

	global handlers
	handlers = Handlers(client, admins, youtube_token)

	print("logging in...")
	client.run(client_token)

main()
