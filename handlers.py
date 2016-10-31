import discord
import requests

def spotify_get_song_headline(track_id):
	request = requests.get("https://api.spotify.com/v1/tracks/" + track_id)

	try:
		request_json = request.json()
		artist = request_json["artists"][0]["name"]
		title = request_json["name"]
		return (artist + " - " + title)
	except:
		return None

def youtube_search_first_id(api_key, search_term):
	payload = {"key": api_key, "part": "id", "type": "video", "q": search_term, "maxResults": 1} # provide the API key, the search term, and limit results to 1
	request = requests.get("https://www.googleapis.com/youtube/v3/search", params = payload) # make the request to Google's API

	try:
		return request.json()["items"][0]["id"]["videoId"] # parse the request and get the video ID
	except:
		print(request.json()) # TODO: debug message
		return None # return None if the request failed or the response was in an unexpected format

class Handlers:
	def __init__(self, client, admins, youtube_api_key):
		self.client = client
		self.admins = admins
		self.youtube_api_key = youtube_api_key

	def is_admin(self, user):
		return (user.id in self.admins)

	async def handle_imgur_gif_mp4_link(self, naked_url, message):
		updated_link = naked_url + ".gifv"
		await self.client.send_message(message.channel, "automatically reformatted imgur link to gifv" + "\n" + updated_link)
		return True

	async def handle_spotify_track(self, track_id, message):
		await self.client.send_typing(message.channel)

		headline = spotify_get_song_headline(track_id)
		if headline is None:
			await self.client.send_message(message.channel, "failed to retreieve track data from Spotify API!")
			return False

		youtube_id = youtube_search_first_id(self.youtube_api_key, headline)
		if youtube_id is None:
			await self.client.send_message(message.channel, "failed to retreieve search data from YouTube API!")
			return False

		await self.client.send_message(message.channel, "best YouTube guess for Spotify track: '" + headline + "':" + "\n" + "https://www.youtube.com/watch?v=" + youtube_id)
		return True

	async def handle_invite_request(self, message):
		invite_url = discord.utils.oauth_url(self.client.user.id, permissions = discord.Permissions.all())
		await self.client.send_message(message.channel, invite_url)
		return True

	async def handle_shutdown_request(self, message):
		if self.is_admin(message.author):
			await self.client.send_message(message.channel, "shutting down...")
			await self.client.close()
			return True
		else:
			await self.client.send_message(message.channel, "only administrators can shut down the bot!")
			return False
