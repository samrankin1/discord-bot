import discord

class Handlers:
	def __init__(self, client, admins):
		self.client = client
		self.admins = admins

	def is_admin(self, user):
		return (user.id in self.admins)

	async def handle_imgur_gif_link(self, message):
		updated_link = message.content.replace(".gif", ".gifv")
		await self.client.send_message(message.channel, "automatically reformatted gif link to gifv" + "\n" + updated_link)
		return True

	async def handle_imgur_mp4_link(self, message):
		updated_link = message.content.replace(".mp4", ".gifv")
		await self.client.send_message(message.channel, "automatically reformatted mp4 link to gifv" + "\n" + updated_link)
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
