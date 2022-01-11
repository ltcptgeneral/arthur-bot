import asyncio
from asyncio import sleep
from sys import prefix
import discord 
from discord.ext import commands

ffmpeg_options = {
	'options': '-vn'
}

token = None

with open("token", "r") as f:
	token = f.read()
	f.close()

async def determine_prefix(bot, message):
	prefix = None

	with open("prefix", "r") as f:
		prefix = f.read()
		f.close()

	return prefix

def determine_roleid():
	roleid = None

	with open("roleid", "r") as f:
		roleid = int(f.read())
		f.close()

	return roleid

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = determine_prefix, description='very cool', intents = intents)

@bot.event
async def on_ready():
	print('Logged in as {0} ({0.id})'.format(bot.user))
	print('------')


@bot.command()
async def setprefix(ctx, *arg):
	if(len(arg) != 1):
		await ctx.send("usage: setprefix <prefix>")

	else:
		prefix = arg[0]

		with open("prefix", "w") as f:
			f.write(prefix)
			f.close()

		await ctx.send("set prefix to: {0}".format(prefix))

@bot.command()
async def setrole(ctx, *arg: discord.Role):
	if(len(arg) != 1):
		await ctx.send("usage: setrole @<rolename>")

	else:
		roleid = arg[0].id

		with open("roleid", "w") as f:
			f.write(str(roleid))
			f.close()

		await ctx.send("set followable role to {0}".format(arg[0]))

@bot.event
async def on_voice_state_update(member, before, after):

	roleid = determine_roleid()

	if((member.id == bot.user.id) or (member.bot) or (roleid not in [role.id for role in member.roles]) or (before.channel == after.channel) or (after.channel == None)):
		pass

	else:

		print("member {0} changed from {1} to {2}".format(member.id, before.channel, after.channel))
		channel = after.channel
		bot_connection = member.guild.voice_client

		if bot_connection:
			await bot_connection.move_to(channel)
		else:
			bot_connection = await channel.connect()

		def after(e):
			print(str(e))

		bot_connection.play(discord.FFmpegPCMAudio("sample.mp3"), after=lambda e: print('Player error: %s' % e) if e else None)

		while bot_connection.is_playing():
			await sleep(0.01)

		await bot_connection.disconnect()

bot.run(token)