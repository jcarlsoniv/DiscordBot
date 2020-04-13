import os
import discord
#import pandas as pd
import mafia as mf
#import test as tst

from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix = '*')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the Discord server!')


game = mf.Game()
#game = tst.Game()
#playerlist = mf.PlayerList()


@bot.command(name = 'play-mafia')
async def play_mafia(ctx, numTown = game.numTown, numMafia = game.numMafia):
    author = ctx.author.name
    user = ctx.author
    channel = ctx.channel
   
    await game.startGame(author, user, channel, numTown, numMafia)

@bot.command(name = 'end-mafia')
async def end_mafia(ctx):
    author = ctx.author.name
    user = ctx.author
    channel = ctx.channel
   
    await game.stopGame(author, user, channel)

@bot.command(name = 'in')
async def opt_in(ctx):
    #mention = ctx.author.mention
    player = ctx.author.name
    user = ctx.author
    channel = ctx.channel

    await game.addPlayer(player, channel, user)

@bot.command(name = 'out')
async def opt_out(ctx):
    player = ctx.author.name
    channel = ctx.channel

    await game.removePlayer(player, channel)

@bot.command(name = 'player-list')
async def player_list(ctx):
    channel = ctx.channel
    
    await game.getPlayerList(channel)

@bot.command(name = 'vote')
async def vote(ctx, target):
    player = ctx.author.name
    channel = ctx.channel

    await game.newVote(channel, player, target)

@bot.command(name = 'unvote')
async def unvote(ctx):
    player = ctx.author.name
    channel = ctx.channel

    await game.removeVote(channel, player)

@bot.command(name = 'vote-count')
async def vote_count(ctx):
    channel = ctx.channel

    await game.voteCount(channel)


@bot.command(name = 'force-kill')
async def force_kill(ctx, target):
    player = ctx.author.name
    channel = ctx.channel

    await game.killPlayer(channel, player)

#testing command (?)
#@bot.command(name = 'team-list')
#async def team_list(ctx):
#    #pull into a function
#    if game.gameStatus == 'Inactive':
#        await ctx.send('A game has not been started yet. Type *play-mafia to start one.')
#    else:
#        await ctx.send(f'Team list is now {game.teamList}')

#testing command (?)
@bot.command(name = 'role-list')
async def role_list(ctx):
    channel = ctx.channel

    await game.getRoleList(channel)

@bot.command(name = 'assign-teams')
async def assign_teams(ctx):
    channel = ctx.channel

    await game.assignTeams(channel)  


    
#testing command (?)
#@bot.command(name = 'user-roles')
#async def user_roles(ctx):
#    user = ctx.author
#    channel = ctx.channel

#    await game.getPlayerRoles(user, channel)

#testing command (?)
@bot.command(name = 'start-day')
async def start_day(ctx):
    #user = ctx.author
    channel = ctx.channel

    await game.startDay(channel)

#testing command (?)
@bot.command(name = 'start-night')
async def start_night(ctx):
    #user = ctx.author
    channel = ctx.channel

    await game.startNight(channel)

#testing command (?)
@bot.command(name = 'phase-change')
async def phase_change(ctx):
    #user = ctx.author
    channel = ctx.channel

    await game.phaseChange(channel)


#testing command (?)
@bot.command(name = 'vote-list')
async def vote_list(ctx):
    channel = ctx.channel

    await game.getVoteList(channel)

bot.run(TOKEN)