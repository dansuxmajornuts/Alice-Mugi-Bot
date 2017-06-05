import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import os



recipe_categories = ["chicken", "pizza", "cocktails", "pasta", "burgers", "sandwiches", "desserts", "salad"]
recipe_urls = {
	"chicken"    : "http://www.seriouseats.com/tags/recipes/chicken",
	"pizza"      : "http://www.seriouseats.com/tags/recipes/pizza",
	"cocktails"  : "http://www.seriouseats.com/recipes/topics/meal/drinks/cocktails",
	"pasta"      : "http://www.seriouseats.com/tags/recipes/pasta",
	"burgers"    : "http://www.seriouseats.com/tags/recipes/burger",
	"sandwiches" : "http://www.seriouseats.com/sandwiches",
	"desserts"   : "http://www.seriouseats.com/desserts",
	"salad"      : "http://www.seriouseats.com/tags/recipes/salad"
}

alice_gifs = [
"https://s-media-cache-ak0.pinimg.com/originals/78/f5/8e/78f58e593a193d470add8983973ee8c4.gif",
"https://68.media.tumblr.com/de6d2ca14fc64f3b4bc73e3651bf5ab3/tumblr_nt5tg2WBcS1r60zuio1_500.gif",
"https://s-media-cache-ak0.pinimg.com/originals/de/83/2d/de832de0340706a16d1b64321850f95e.gif",
"http://pa1.narvii.com/5939/4d3eeb22212ff56d5e30b9b7596fa29d8dbad042_hq.gif",
"https://media.giphy.com/media/13ZoPdc5aFQM5q/giphy.gif",
"https://media.tenor.com/images/7735c516c3c0c5896f4c2cbd969c187e/tenor.gif",
"http://pa1.narvii.com/6163/74711fb8f84cb1b93e04ef6c9d27995a72dc93cd_hq.gif",
"http://pa1.narvii.com/6024/ee7acf9fccff51e7b8e05b9133e9ba9976053458_hq.gif",
"http://i.imgur.com/iyARgYd.gif",
"http://i.imgur.com/H0l6Mlb.gifv",
"http://i43.photobucket.com/albums/e374/NeoRyo/JapaneseAnime/Shokugeki%20no%20Soma/Shokugeki%20no%20Soma%20-%20Episode%2013%20-%20Nakiri%20Alice%20teaches%20Ryou%20how%20to%20intimidate%20people.gif"
]



description = '''Alice Nakiri on duty!'''

bot = commands.Bot(command_prefix='?', description=description, pm_help=True)

member_points = {}
db_filename = "AliceBotPoints.sqlite"


async def point_counter():
	currently_online = set()
	members_list = bot.get_all_members()
	for member in members_list:
		if member.bot:
			continue
		if member.voice.voice_channel is not None and not member.voice.is_afk:
			currently_online.add(member)

	conn = sqlite3.connect(db_filename)
	c = conn.cursor()
	for member in currently_online:
		member_points[member.id] = member_points.get(member.id, 0) + 10
		c.execute("INSERT or REPLACE into points_table (id, points) VALUES (%s, %s)" % (member.id, member_points[member.id]))
	conn.commit()
	conn.close()


async def db_init():
	conn = sqlite3.connect(db_filename)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS points_table (id INTEGER PRIMARY KEY, points INTEGER)')
	users = c.execute('SELECT id, points from points_table').fetchall()
	for user in users:
		member_points[str(user[0])] = user[1]
	conn.commit()
	conn.close()


@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(game=discord.Game(name='?help for commands'))
	await db_init()

	while True:
		await point_counter()
		await asyncio.sleep(300)


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if "alice" in message.content.lower() :
		await bot.send_message(message.channel, "https://s-media-cache-ak0.pinimg.com/originals/0a/92/d7/0a92d7d7f15ba1e4e14449ec29271cb7.gif")
		await bot.send_message(message.channel, "Stop talking about me!")

	await bot.process_commands(message)


@bot.command()
async def gifme():
	"""Shows a random enjoyable gif. """
	await bot.say(random.choice(alice_gifs))


@bot.command()
async def recipe(request_category : str):
	"""Links a random recipe from SeriousEats. Recipe options are: chicken, pizza, cocktails, pasta, burgers, sandwiches, desserts, salad, or random
	"""
	request_category = request_category.lower()
	if request_category == "random":
		recipe_category = random.choice(recipe_categories)
	elif request_category in recipe_categories:
		recipe_category = request_category
	else:
		await bot.say("Incorrect category, choose one of [chicken, pizza, cocktails, pasta, burgers, sandwiches, desserts, salad, random]")
		return

	async with aiohttp.get(recipe_urls[recipe_category]) as resp:
		if resp.status == 200:
			webpage = await resp.text()
		else:
			bot.say("File not found")


	recipe_recommendations = []
	soup = BeautifulSoup(webpage, "html.parser")
	for link in soup.find_all('a', {"class" : "module__image-container module__link"}):
		recipe_link = link.get('href')
		if recipe_link != recipe_urls[recipe_category]:
			recipe_recommendations.append(recipe_link)
	await bot.say(random.choice(recipe_recommendations))


@bot.command(pass_context=True)
async def bentos(ctx):
	""" Shows how many Bentos you have! """
	sender_id = ctx.message.author.id
	if sender_id in member_points:
		await bot.say("You currently have " + str(member_points[sender_id]) + " Bentos.")
	else:
		await bot.say("You currently have no Bentos, get cooking!")



bot.run('MzE5NzM5ODYxOTc4MzE2ODEw.DBFcug.6H82mGImZexQHyuujZyJKqI9TpQ')
