from asyncio import sleep
from sys import prefix
import discord 
from discord.ext import commands
import random

from config import *

config_path = "config.json"

ffmpeg_options = {
	'options': '-vn'
}

config = {}
x = load_config(config_path, config)
if x == 1:
	print('Failed to load config, exiting')
	exit(1)
token = config['guild']['token']
prefix = config['guild']['prefix']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = prefix, description='very cool', intents = intents)
bot.config = config

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

		bot.config['guild']['prefix'] = prefix
		save_config(config_path, bot.config)

		await ctx.send("set prefix to: {0}".format(prefix))

@bot.command()
async def setrole(ctx, *arg: discord.Role):
	if(len(arg) != 1):
		await ctx.send("usage: setrole @<rolename>")

	else:
		roleid = arg[0].id

		bot.config['guild']['roleid'] = prefix
		save_config(config_path, bot.config)

		await ctx.send("set followable role to {0}".format(arg[0]))

async def play_recursive(vc, target):

	if(target == None):
		return

	samples = bot.config['samples']

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

		samples = bot.config['samples']

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
	
	roleid = bot.config['guild']['roleid']

	if((member.id == bot.user.id) or (member.bot) or (roleid not in [role.id for role in member.roles]) or (before.channel == after.channel) or (after.channel == None)):
		return

	else:
		channel = member.voice.channel
		vc = await channel.connect()
		
		samples = bot.config['samples']

		ordered_samples = []
		ordered_weights = []

		for key, sample in samples.items():
			ordered_samples.append(key)
			ordered_weights.append(sample["weight"])

		choice = random.choices(ordered_samples, ordered_weights, k = 1)[0]

		await sleep(0.5)

		await play_recursive(vc, choice)

		while vc.is_playing():
			await sleep(0.01)

		await sleep(0.5)

		await vc.disconnect()

bot.run(token)