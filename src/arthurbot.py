import asyncio
from asyncio import sleep
from sys import prefix
import discord 
from discord.ext import commands
import random

from config import get_samples, get_token, get_prefix, get_roleid

config_path = "config.json"

ffmpeg_options = {
	'options': '-vn'
}

token = get_token(config_path)

async def determine_prefix(bot, message):
	return get_prefix(config_path)

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

async def play_recursive(vc, target):

	if(target == None):
		return

	samples = get_samples(config_path)

	prefixes = samples[target]["prefix"]
	prefix_name = []
	prefix_weight = []
	for p in prefixes:
		prefix_name.append(p["name"])
		prefix_weight.append(p["weight"])

	prefix_choice = random.choices(prefix_name, prefix_weight, k = 1)[0]

	await play_recursive(vc, prefix_choice)

	print("playing " + target)

	vc.play(discord.FFmpegPCMAudio(samples[target]["path"]), after=lambda e: print('Player error: %s' % e) if e else None)

	while vc.is_playing():
		await sleep(0.01)

	suffixes = samples[target]["suffix"]
	suffix_name = []
	suffix_weight = []
	for p in suffixes:
		suffix_name.append(p["name"])
		suffix_weight.append(p["weight"])

	suffix_choice = random.choices(suffix_name, suffix_weight, k = 1)[0]

	await play_recursive(vc, suffix_choice)

	return 

@bot.command()
async def testonce(ctx, *arg):

	if(len(arg) != 1):
		await ctx.send("usage: playonce <soundfile>")

	elif(ctx.author.voice == None):
		await ctx.send("you're not in a voice channel")

	else:

		await ctx.author.voice.channel.connect()

		choice = arg[0]

		ctx.voice_client.play(discord.FFmpegPCMAudio(choice), after=lambda e: print('Player error: %s' % e) if e else None)

		while ctx.voice_client.is_playing():
			await sleep(0.01)

		await ctx.voice_client.disconnect()

@bot.command()
async def playonce(ctx, *arg):

	if(len(arg) != 0):
		await ctx.send("usage: playonce")

	elif(ctx.author.voice == None):
		await ctx.send("you're not in a voice channel")

	else:

		vc = await ctx.author.voice.channel.connect()

		samples = get_samples(config_path)

		ordered_samples = []
		ordered_weights = []

		for key, sample in samples.items():
			ordered_samples.append(key)
			ordered_weights.append(sample["weight"])

		choice = random.choices(ordered_samples, ordered_weights, k = 1)[0]

		await play_recursive(vc, choice)

		while vc.is_playing():
			await sleep(0.01)

		await vc.disconnect()

@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
	vc_before = before.channel
	vc_after = after.channel
	
	roleid = get_roleid(config_path)

	if((member.id == bot.user.id) or (member.bot) or (roleid not in [role.id for role in member.roles]) or (before.channel == after.channel) or (after.channel == None)):
		return

	else:
		channel = member.voice.channel
		vc = await channel.connect()
		
		samples = get_samples(config_path)

		ordered_samples = []
		ordered_weights = []

		for key, sample in samples.items():
			ordered_samples.append(key)
			ordered_weights.append(sample["weight"])

		choice = random.choices(ordered_samples, ordered_weights, k = 1)[0]

		await play_recursive(vc, choice)

		while vc.is_playing():
			await sleep(0.01)

		await vc.disconnect()

bot.run(token)