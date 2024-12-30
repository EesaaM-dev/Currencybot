import asyncio
import os
import random

import aiosqlite
import discord
from discord.ext import commands

from keep_alive import keep_alive

bet = 0
admin_id = "824687357302800436"
x = 0
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!",
                   intents=intents,
                   case_insensitive=True,
                   help_command=None)


@bot.event
async def on_ready():
  print('Ready!')
  global botdb
  botdb = await aiosqlite.connect("bank.db")
  await asyncio.sleep(3)
  async with botdb.cursor() as c:
    await c.execute(
        "CREATE TABLE IF NOT EXISTS bank(wallet INTEGER, bank INTEGER, user TEXT)"
    )
  await botdb.commit()
  print("database ready")


async def createbal(user_id):
  botdb = await aiosqlite.connect("bank.db")
  async with botdb.cursor() as c:
    print("testing")
    await c.execute("INSERT INTO bank VALUES(?,?,?)", (0, 100, user_id))
    print("???")
    await botdb.commit()


async def updatewall(user_id, amount):
  botdb = await aiosqlite.connect("bank.db")

  async with botdb.cursor() as c:
    await c.execute("SELECT wallet, bank FROM bank WHERE user=?", (user_id, ))
    data = await c.fetchone()
    if data is None:
      await createbal(user_id)
      return True
    print(data[0], data[1])
    await c.execute("UPDATE bank SET wallet=? WHERE user=?", (
        data[0] + amount,
        user_id,
    ))
  await botdb.commit()
  print("wallet updated")
  print(data[0], data[1])


async def updatebank(user_id, amount):
  botdb = await aiosqlite.connect("bank.db")

  async with botdb.cursor() as c:
    await c.execute("SELECT wallet, bank FROM bank WHERE user=?", (user_id, ))
    data = await c.fetchone()
    if data is None:
      await createbal(user_id)
      return True
    print(data[0], data[1])
    await c.execute("UPDATE bank SET bank=? WHERE user=?", (
        data[1] + amount,
        user_id,
    ))
  await botdb.commit()
  print("bank updated")
  print(data[0], data[1])


async def depbal(user_id, amount):
  botdb = await aiosqlite.connect("bank.db")

  async with botdb.cursor() as c:
    await c.execute("SELECT wallet, bank FROM bank WHERE user=?", (user_id, ))
    data = await c.fetchone()
    if data is None:
      await createbal(user_id)
      return True
    print(data[0], data[1])
    await c.execute("UPDATE bank SET bank=? WHERE user=?", (
        data[1] + int(amount),
        user_id,
    ))
    await c.execute("UPDATE bank SET wallet=? WHERE user=?", (
        data[0] - int(amount),
        user_id,
    ))
  await botdb.commit()
  print("bank updated")
  print(data[0], data[1])


async def withbal(user_id, amount):
  botdb = await aiosqlite.connect("bank.db")

  async with botdb.cursor() as c:
    await c.execute("SELECT wallet, bank FROM bank WHERE user=?", (user_id, ))
    data = await c.fetchone()
    if data is None:
      await createbal(user_id)
      return True
    print(data[0], data[1])
    await c.execute("UPDATE bank SET wallet=? WHERE user=?", (
        data[0] + int(amount),
        user_id,
    ))
    await c.execute("UPDATE bank SET bank=? WHERE user=?", (
        data[1] - int(amount),
        user_id,
    ))

  await botdb.commit()
  print("withdrawn to wallet")


async def getbal(user_id):
  botdb = await aiosqlite.connect("bank.db")
  async with botdb.cursor() as c:
    await c.execute("SELECT wallet, bank FROM bank WHERE user=?", (user_id, ))
    data = await c.fetchone()
    if data is None:
      await createbal(user_id)
      return 0, 0
      return True
    return data


@bot.command()
@commands.cooldown(1, 30, commands.cooldowns.BucketType.user)
async def beg(ctx):
  user_id = str(ctx.author.id)
  donation = random.randint(1, 50)
  await ctx.send(f"you were given: {donation}")
  await updatewall(user_id, donation)


@beg.error
async def beg_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(f"you are on cooldown for {error.retry_after:.0f}s")


@bot.command()
async def help(ctx):
  embed = discord.Embed(
      title="Commands",
      description=
      "**!cf <amount> <choice>**   this command allows the user to bet on a coinflip of heads or tails\n\n                                                                                                                       **!chance <amount> <chance>** this command allows the user to bet on 50, 25, 10, 5 or 1 odds\n\n**!bal <user>** displays users wallet and bank use !bal without \"<user>\" to see own balance\n\n**!dep <amount>** deposits the amount specified into the users bank\n\n**!beg** this command allows the user to beg for money a random amount is generated from between 1 and 50",
      colour=0x3af2a3)

  await ctx.send(embed=embed)


@bot.command()
async def cf(ctx, bet, answer):
  coin_flip = random.choice(["h", "t"])
  user_id = str(ctx.author.id)
  wallet, bank = await getbal(user_id)
  print("your bank is", bank)
  print("your wallet is", wallet)
  print("your bet is", bet)

  if bet == "all" or bet == "max":
    bet = wallet

  if int(wallet) < int(bet):
    await ctx.reply("insufficient funds")
  elif int(wallet) == 0:
    await ctx.reply("you have 0")

  elif int(bet) < 0:
    await ctx.reply("illegal action")

  else:

    if answer == "":
      await ctx.reply("invalid input try again")

    if coin_flip == answer:
      x = int(bet)
      xtemp = int(bet)

      await ctx.reply(
          f'**congratulations you won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)
    elif answer != "h" and answer != "t":
      await ctx.reply("invalid answer")
    else:
      y = int(bet)
      bet = -int(bet)

      await updatewall(user_id, bet)
      await ctx.reply(
          f'**sorry you you have lost {y:,} <:emerald:1165299505730695301> **')


@bot.command()
async def chance(ctx, bet, answer):
  chancepercent = random.randint(1, 100)
  user_id = str(ctx.author.id)
  wallet, bank = await getbal(user_id)
  print("your bank is", bank)
  print("your wallet is", wallet)
  print("your bet is", bet)
  if bet == "all" or bet == "max":
    bet = wallet

  if int(wallet) < int(bet):
    await ctx.reply("insufficient funds")
  elif int(wallet) == 0:
    await ctx.reply("you have 0")

  elif int(bet) < 0:
    await ctx.reply("illegal action")

  else:

    if answer == "":
      await ctx.reply("invalid input try again")

    elif answer == "50" and chancepercent <= 50:
      x = int(bet)
      xtemp = int(bet) * 2

      await ctx.reply(
          f'**congratulations you won chance 50 you have won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)
    elif answer == "25" and chancepercent <= 25:
      x = int(bet) * 3
      xtemp = int(bet) * 4

      await ctx.reply(
          f'**congratulations you won chance 25 you have won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)

    elif answer == "10" and chancepercent <= 10:
      x = int(bet) * 9
      xtemp = int(bet) * 10
      await ctx.reply(
          f'**congratulations you won chance 10 you have won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)

    elif answer == "5" and chancepercent <= 5:
      x = int(bet) * 19
      xtemp = int(bet) * 20
      await ctx.reply(
          f'**congratulations you won chance 5 you have won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)

    elif answer == "1" and chancepercent == "1":
      x = int(bet) * 99
      xtemp = int(bet) * 100
      await ctx.reply(
          f'**congratulations you won chance 1 you have won {xtemp:,}<:emerald:1165299505730695301> **'
      )
      await updatewall(user_id, x)

    elif answer != "25" and answer != "50" and answer != "10" and answer != "5" and answer != "1":
      await ctx.reply("**invalid answer**")
    else:
      y = int(bet)
      bet = -int(bet)

      await updatewall(user_id, bet)
      await ctx.reply(
          f'**sorry you lose {y:,} <:emerald:1165299505730695301> **')


@bot.command()
async def bal(ctx, user: discord.Member = None):
  if user is None:
    user_id = str(ctx.author.id)
  else:
    author = str(ctx.author.id)
    user_id = str(user.id)

    print(author)
    print(user_id)
  wallet, bank = await getbal(user_id)
  walletfor = '{:,}'.format(wallet)
  bankfor = '{:,}'.format(bank)

  print(wallet, bank)
  await ctx.reply(
      f"**wallet: {walletfor}<:emerald:1165299505730695301> bank: {bankfor}<:emerald:1165299505730695301>**"
  )


@bot.command()
async def ez(ctx):
  user_id = str(ctx.author.id)
  ezmoney = 25000

  await ctx.send(
      f"**you were given {ezmoney:,}<:emerald:1165299505730695301>**")
  await updatewall(user_id, ezmoney)


@bot.command()
async def give_(ctx, user: discord.Member, amount):
  user_id = str(user.id)
  author = str(ctx.author.id)
  print(author)
  print(user_id)
  if int(amount) <= 0:
    await ctx.send("amount cannot be below 0")
  else:
    if author == admin_id:
      user_id = str(user.id)
      amount = int(amount)
      await ctx.send(f"{user.mention} you were given: {amount:,}")
      await updatewall(user_id, int(amount))
    else:
      await ctx.send(user.mention + " get shit on kid")


@bot.command()
async def wipe(ctx, user: discord.Member):
  #found max account balance value at  9,223,372,036,854,775,807
  user_id = str(user.id)
  author = str(ctx.author.id)
  print(author)
  print(user_id)
  wallet, bank = await getbal(user_id)
  wallamount = -int(wallet)
  bankamount = -int(bank)
  print(wallamount)
  print(bankamount)
  print(wallet)
  print(bank)

  if author == admin_id:
    user_id = str(user.id)
    await ctx.send("get wiped kid")
    await updatewall(user_id, wallamount)
    await updatebank(user_id, bankamount)
  else:
    await ctx.send(user.mention + " was succesfully wiped")
    await asyncio.sleep(3)
    await ctx.send("JK")


@bot.command()
async def slap(ctx, user: discord.Member):
  slapgif = [
      "https://media0.giphy.com/media/vi2ciYHi5u0FO/giphy.gif?cid=ecf05e47ta9e9nc24uyszwi7t874zy4pgv6dc6yb45f9hm81&ep=v1_gifs_search&rid=giphy.gif&ct=g",
      "https://media0.giphy.com/media/mEtSQlxqBtWWA/giphy.gif?cid=ecf05e477a3rn6etdwler7y9nhkzm7hkz97kal9fjqbo2gna&ep=v1_gifs_search&rid=giphy.gif&ct=g",
      "https://media3.giphy.com/media/9U5J7JpaYBr68/giphy.gif?cid=ecf05e47sbm7q4g0ntzam2agoat7docgypqwx8jqs6geeu5p&ep=v1_gifs_related&rid=giphy.gif&ct=g",
      "https://media0.giphy.com/media/Qumf2QovTD4QxHPjy5/giphy.gif?cid=ecf05e477a3rn6etdwler7y9nhkzm7hkz97kal9fjqbo2gna&ep=v1_gifs_search&rid=giphy.gif&ct=g"
  ]
  embed = discord.Embed(title="Slap test",
                        colour=0x2ea873,
                        description="you got slapped")
  select1 = random.choice(slapgif)
  print(select1)
  embed.set_image(url=select1)

  await ctx.send("get slapped nerd " + user.mention)
  await ctx.send(embed=embed)


@bot.command(name="with")
async def withdraw(ctx, amount):
  user_id = str(ctx.author.id)
  wallet, bank = await getbal(user_id)
  if amount == "all" or amount == "max":
    amount = bank
    print(amount)
    print("all has been invoked")
  if int(amount) > int(bank) or int(amount) == 0 or int(amount) < 0 or int(
      bank) == 0:
    amount = int(amount)
    await ctx.reply(
        f'**you cannot withdraw {amount:,} <:emerald:1165299505730695301> to your bank**'
    )
  else:
    await withbal(user_id, amount)
    amount = int(amount)
    await ctx.reply(
        f'**you have withdrawn {amount:,} <:emerald:1165299505730695301> to your bank**'
    )


@bot.command()
async def dep(ctx, amount):
  user_id = str(ctx.author.id)
  wallet, bank = await getbal(user_id)
  if amount == "all" or amount == "max":
    amount = wallet
    print(amount)
    print("all has been invoked")
  if int(amount) > int(wallet) or int(wallet) == 0 or int(amount) < 0 or int(
      amount) == 0:
    amount = int(amount)
    await ctx.reply(
        f'**cannot deposit {amount:,} <:emerald:1165299505730695301> to your bank**'
    )

  else:
    await depbal(user_id, amount)
    amount = int(amount)
    await ctx.reply(
        f'**you have deposited {amount:,} <:emerald:1165299505730695301> to your bank**'
    )


my_secret = os.environ['BOT_TOKEN']
keep_alive()
bot.run(my_secret)
