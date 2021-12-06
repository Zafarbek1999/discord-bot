import os

from dotenv import load_dotenv
import discord
from discord.ext import commands
import redis

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

r = redis.Redis()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    r.set(str(member), 0)
    await member.guild.system_channel.send(f'{member.name} connected to the channel.')


@bot.event
async def on_member_remove(member):
    r.delete(str(member))
    await member.guild.system_channel.send(f'{member.name} left channel.')


@bot.event
async def on_message(ctx):
    print(ctx)
    author = ctx.author
    cnt = r.get(str(author))
    if cnt is not None:
        cnt = int(cnt) + 1
    else:
        cnt = 1
    if cnt % 20 == 0:
        embed = discord.Embed(title=f":chart_with_upwards_trend: Congratulations {author.name}!",
                              description=f"Your level is up to {cnt // 20}!")
        await ctx.channel.send(embed=embed)
    r.set(str(author), cnt)


@bot.command()
async def helpcmd(ctx):
    await ctx.send(f'Hello')


# The below code kicks member.
@commands.has_permissions(kick_members=True)
@bot.command(name='kick')
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    print(ctx)
    if member is None or member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
        return
    await member.kick(reason=reason)
    embed = discord.Embed(title=f":boot: Kicked {member.name}!",
                          description=f"Reason: {reason}\nBy: {ctx.author.mention}")
    await ctx.message.delete()
    await ctx.channel.send(embed=embed)
    r.delete(str(member))


# The below code bans member.
@commands.has_permissions(ban_members=True)
@bot.command(name='ban')
async def ban(ctx, *, member: discord.User = None, reason="No reason provided"):
    if member is None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    embed = discord.Embed(title=f":x: Banned {member.name}!",
                          description=f"Reason: {reason}\nBy: {ctx.author.mention}")
    await ctx.guild.ban(member, reason=reason)
    await ctx.channel.send(embed=embed)
    r.delete(str(member))


# The below code unbans member.
@commands.has_permissions(administrator=True)
@bot.command(name='unban')
async def unban(ctx, *, member, reason="No reason provided"):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.id == int(member[3:-1]):
            embed = discord.Embed(title=f":white_check_mark: Unbanned {user.name}.",
                                  description=f"Reason: {reason}\nBy: {ctx.author.mention}")
            await ctx.guild.unban(user)
            await ctx.channel.send(embed=embed)
            return
    await ctx.channel.send('This user is not banned.')


bot.run(TOKEN)
