import os
import random
import discord
import pandas as pd
import time
import copy

from dotenv import load_dotenv

GUILD = os.getenv('DISCORD_GUILD')


class Game:
    
    def __init__(self, GameType = 'Standard'):
        self.serverID = GUILD
        #self.gameID = 
        self.gameType = GameType
        self.gameStatus = 'Inactive'  #Status order -> Inactive, Setup, In Progress, Complete
        self.gameHost = ''
        self.gameEnd = ''
        self.endReason = ''
        self.dayCounter = 0
        self.nightCounter = 0
        self.phaseTime = 0
        self.phaseLength = 10
        self.gameStart = ''
        self.playerList = []
        self.teamList = []
        self.roleList = []
        self.voteList = []
        self.runningVotesDict = {'Player':[],'Voters':[]}
        self.voteCounter = pd.DataFrame(columns = ['Player', 'Votes'])
        self.numTown = 1
        self.numMafia = 1
        self.numDoc = 1
        self.numCop = 1
        self.numGodfather = 1
        self.lynchTarget = '' # make a Player object?
        #If you add things to the above list, check if it needs to be added to stopGame


    #async def checkGameRunning(self):
    #    return self.gameStatus
    

    async def startSetup(self, author, user, channel, numTown: int, numMafia: int):
        
        #Check Mafia <= Town/2
        
        if self.gameStatus == 'Active':
            await channel.send(f'A game is already active in {channel}. Type *in to join. Type *end-mafia to end the game.')
        elif self.gameStatus == 'Inactive':
            self.gameStatus = 'Active'
            self.numTown = numTown
            self.numMafia = numMafia


            #Set game initiator as mafia host
            ###Actually implement Mafia Host role
            self.gameHost = user
            #discordRole = discord.utils.get(user.guild.roles, name = 'Mafia Host')
            #await user.add_roles(discordRole)

            #Populate teamList
            tT = 0
            while tT < numTown:
                self.teamList.append('Town')
                tT += 1
            
            mT = 0
            while mT < numMafia:
                self.teamList.append('Mafia')
                mT += 1

            #Populate roleList
            while len(self.roleList) < len(self.teamList):
                mR = 0
                gfCount = 0
                while mR < numMafia:
                    if gfCount < self.numGodfather:
                        self.roleList.append(Role('Godfather','Mafia'))
                        gfCount += 1
                    else:
                        self.roleList.append(Role('Goon', 'Mafia'))
                    mR += 1
                
                tR = 0
                copCount = 0
                docCount = 0
                while tR < numTown:
                    if copCount < self.numCop:
                        self.roleList.append(Role('Cop','Town'))
                        copCount += 1
                    elif docCount < self.numDoc:
                        self.roleList.append(Role('Doctor','Town'))
                        docCount += 1
                    else:
                        self.roleList.append(Role('Vanilla Townie','Town'))
                    tR += 1
                
            await channel.send(f'{author} has started a game of mafia ({numTown} Town, {numMafia} Mafia) in {channel}. Type *in to join.')


    async def stopGame(self, author, user, channel):
        #Add check so only host can end game.
        if self.gameStatus == 'Active':
            self.gameStatus = 'Inactive'
            if self.dayCounter > self.nightCounter:
                self.gameEnd = f'Day {self.dayCounter}'
            else:
                self.gameEnd = f'Night{self.nightCounter}'
            self.dayCounter = 0
            self.nightCounter = 0
            self.phaseTime = 0
            self.playerList = []
            self.teamList = []
            self.roleList = []
            self.voteList = []
            self.runningVotesDict = {'Player':[],'Voters':[]}

            #Remove game initiator as mafia host
            ###Actually implement Mafia Host role
            self.gameHost = ''
            #discordRole = discord.utils.get(user.guild.roles, name = 'Mafia Host')
            #await user.remove_roles(discordRole)

            await channel.send(f'{author} has stopped the game of mafia in {channel}. Type *start-game to start a new one.')
        elif self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')


    async def addPlayer(self, player, channel, user):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        elif (len(self.playerList) == (self.numTown + self.numMafia)):
            await channel.send('The sign-up list is full - cannot add any more players.')
        elif any(p.name == player for p in self.playerList):
                await channel.send(f'{player} is already in the game.')
        else:
            newPlayer = Player(player, user)
            self.playerList.append(newPlayer)
            await channel.send(f'Adding {player} to the game.')


    async def removePlayer(self, player, channel):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        elif not any(p.name == player for p in self.playerList):
            await channel.send(f'{player} is not in the game.')
        else:
            for p in self.playerList:
                if p.name == player:
                    self.playerList.remove(p)
                    await channel.send(f'Removing {player} from the game.')


    async def getPlayerList(self, channel):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        else:
            await channel.send([f'{player}' for player in self.playerList])


    async def getRoleList(self, channel):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        else:
            await channel.send([f'{role}' for role in self.roleList])


    async def assignTeams(self, channel):  
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        else:
            roleAssignmentList = self.roleList.copy()

            for p in self.playerList:
                p.role = Role()
                role = random.choice(roleAssignmentList)
                p.role = role
                roleAssignmentList.remove(role)

            for p in self.playerList:
                if p.role.team == 'Mafia':
                    await p.playerID.create_dm()
                    await p.playerID.dm_channel.send(f'Your role is {p.role}! ')
                    if self.numMafia > 1:
                        await p.playerID.dm_channel.send('You are on a team with:')
                        await p.playerID.dm_channel.send('\n'.join([f'{q.name} ({q.role.name})' for q in self.playerList if (q.role.team == 'Mafia' and q.name != p.name)]))
                if p.role.team == 'Town':
                    await p.playerID.create_dm()
                    await p.playerID.dm_channel.send(f'Your role is {p.role}! Hunt down those scum!')

            await channel.send('Roles have been assigned. Alert the proper authorities if you did not receive a role.')


    ###Actually implement Mafia Host role
    #async def getPlayerRoles(self, user, channel):
        #discordRoles = discord.utils.get(user.roles)
        #await channel.send(discordRoles)


        ###################################################################


    async def startDay(self, channel):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        #elif self.gameStatus == 'Setup':
            #await channel.send('The game is currently being setup. Type *begin-game to begin.')
        #elif self.gameStatus == 'In Progress':
        else:
            self.dayCounter += 1

            for p in self.playerList:
                p.hasVoted = False

                if await self.checkPlayerAlive(p):
                    self.voteList.append(Vote(self.dayCounter, p.name))
                

            await channel.send(f'Day {self.dayCounter} has begun.  Lynch some scum.')


    async def startNight(self, channel):
        if self.gameStatus == 'Inactive':
            await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        #elif self.gameStatus == 'Setup':
            #await channel.send('The game is currently being setup. Type *begin-game to begin.')
        #elif self.gameStatus == 'In Progress':
        else:
            self.nightCounter += 1

            await channel.send(f'Night {self.nightCounter} has begun.  Submit your actions.')


    async def phaseChange(self, channel):
        #Reinitialize daily variables.
        self.runningVotesDict = {'Player':[],'Voters':[]}
        for p in self.playerList:
            p.hasVoted = False

        if self.dayCounter > self.nightCounter:
            await self.startNight(channel)
        else:
            await self.startDay(channel)


    async def runGame(self, channel):
        self.gameStart = time.time()
        phaseEndTime = copy.copy(self.gameStart)

        await self.startDay(channel)

        x = 0

        #WIN CONDITION CHECK
        while x < 4:
            elapsed = 0
            while elapsed < self.phaseLength:
                elapsed = time.time() - phaseEndTime
                #await channel.send(f'{elapsed} elapsed.')
                time.sleep(1)

            await self.phaseChange(channel)
            phaseEndTime = time.time()
            x += 1

#########################################################################################################################
    #async def getPhaseTimeRemaining(self, channel):
        


    async def killPlayer(self, channel, player):
        p = await self.getPlayer(player)

        if await self.checkPlayerAlive(p):
            p.isAlive = False
            await channel.send(f'{p.name} has been killed.')
        else:
            await channel.send(f'{p.name} is already dead.')


    async def newVote(self, channel, player, target):
        #add check player alive
        p = await self.getPlayer(player)

        #listOfVotes = []

        

        if await p.checkPlayerVoted():
            await channel.send(f'{player}, you have already voted.  Please *unvote first if you want to change your vote.')
        else:

            for v in self.voteList:
                if (v.voter == player and v.voteDay == self.dayCounter):
                    v.voteTarget = target
                    #if not target in self.voteTargets.values:            ############ FIX THIS SHIT
                    #    self.voteTargets = self.voteTargets.append(pd.DataFrame({'Player': [target], 'Votes': 1}))   
                    #else:
                    #    self.voteTargets.loc[self.voteTargets.Player.isin([target]), 'Votes'] += 1

                    await channel.send(f'{player} has voted for {v.voteTarget}.')

            if not target in self.runningVotesDict['Player']:
                self.runningVotesDict['Player'].append(target)
                #listOfVotes.append(player)
                self.runningVotesDict['Voters'].append([player])
            elif target in self.runningVotesDict['Player']:
                index = self.runningVotesDict['Player'].index(target)
                if not player in self.runningVotesDict['Voters'][index]:
                    self.runningVotesDict['Voters'][index].append(player)
                else:
                    await channel.send(f'{player}, you are already voting for {target}.')

          #################

        #self.voteCounter['Votes'] = self.voteCounter['Votes'].apply(pd.to_numeric)
  
        p.hasVoted = True

        await self.voteCount(channel)

      
####################################################################          



    async def getLynchTarget(self, channel):

            #Need to work through more robust lynchTarget logic - include timestamps from votes?

            self.voteCounter['Votes'] = self.voteCounter['Votes'].apply(pd.to_numeric)

            self.lynchTarget = self.voteCounter.loc[self.voteCounter['Votes'].idxmax()]['Player']

            #return self.lynchTarget
            #await channel.send(f'{self.lynchTarget} is currently up for lynch.')





    async def removeVote(self, channel, player):
        p = await self.getPlayer(player)

        if not await p.checkPlayerVoted():
            await channel.send(f'{player}, you have not voted yet.  Please *vote for a player.')
        else:
            for v in self.runningVotesDict['Voters']:
                index = 0
                if player in v:
                    v.remove(player)
                index += 1 

        await self.voteCount(channel)

        p.hasVoted = False

        await self.getLynchTarget(channel)

        for v in self.voteList:
            if (v.voter == player):
                await channel.send(f'{player} has unvoted for {v.voteTarget}.')
                v.voteTarget = 'no one'
    
        


    async def getVoteList(self, channel):
        #if self.gameStatus == 'Inactive':
            #await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        #else:
        await channel.send([f'{vote}' for vote in self.voteList])
        

    async def getVoteDict(self, channel):
        #if self.gameStatus == 'Inactive':
            #await channel.send('A game has not been started yet. Type *play-mafia to start one.')
        #else:
        await channel.send(self.runningVotesDict)
     
     
    async def voteCount(self, channel):
        #Improve formatting for non-voters
        self.voteCounter = pd.DataFrame(columns = ['Player', 'Votes'])
        voteCountJoined = []
        

        for p in self.runningVotesDict['Player']:
            index = self.runningVotesDict['Player'].index(p)
            listOfVoters = self.runningVotesDict['Voters'][index]
            numVotes = len(listOfVoters)

            self.voteCounter = self.voteCounter.append({'Player': p, 'Votes': pd.to_numeric(numVotes)}, ignore_index = True)
             
            voteCountJoined.append(f'{p} ({numVotes}): ' + ', '.join(lov for lov in listOfVoters))

        voteCountOutput = '\n'.join(voteCountJoined)


        embed = discord.Embed(
            title = f'Day {self.dayCounter} Vote Count',
            color = discord.Color.red()
        )

        embed.set_footer(text = 'Test votecount footer.')
        embed.add_field(name = '---------------------------------', value = f'{voteCountOutput}', inline = False)

        await self.getLynchTarget(channel)
        embed.add_field(name = '---------------------------------', value = f'{self.lynchTarget} is currently up for lynch.', inline = False)
        

        #for vc in self.voteCounter:
        #    embed.add_field(name = vc['Player'][0], value = vc['Votes'][0])

        await channel.send(embed = embed)


        #await channel.send(f'{self.voteCounter}')

        

    #    for v in self.voteList:
    #       if v.voteDay == self.dayCounter and not any(t == v.voteTarget for t in targetList):
    #            targetList.append(v.voteTarget)

    #    for target in targetList:
    #        targetCounter = 0
    #        for v in self.voteList:
    #            if (v.voteTarget == target and v.voteDay == self.dayCounter):
    #                targetCounter += 1
    #        await channel.send(f'{target} ({targetCounter}): ' + ', '.join([v.voter for v in self.voteList if v.voteTarget == target and v.voteDay == self.dayCounter]))
        




#Make this cleaner / clean up other functions
    async def getPlayer(self, player):
        for p in self.playerList:
            if p.name == player:
                return p


    async def checkPlayerAlive(self, player):
        return player.isAlive



###############################################################################################
#######################################   BACKLOG    ##########################################

### TIME-BASED VOTING LIMIT
### LOWER() CHECK ON VOTES
### ADD PHASE STATUS CHECKS FOR ALL ACTIONS
### ADD ALIVE STATUS CHECKS
### DISALLOW VOTES AT NIGHT
### DISALLOW ROLES DURING DAY
### ADD WIN CONDITION CHECKS
### ADD FUNCTION FOR CURRENT DAY'S VOTES
### NO LYNCH VS NO VOTE
### TIME STAMP ON VOTES
### LYNCH TARGET LOGIC
### TURN VOTE LIST INTO FULL AUDIT TRAIL


### TRACK VOTE CHANGES WITHIN THE SAME DAY
### SPECIFIC CHANNEL WITH ALIVE/DEAD ROLES, MUTING DEAD PLAYERS
### MESSAGE FORMATTING

###############################################################################################


class Player:

    def __init__(self,  Name, PlayerID): #, Team): , GameID):
        #self.gameID = 
        self.playerID = PlayerID
        self.name = Name
        self.team = 'Unassigned'
        self.role = Role()
        self.isAlive = True
        self.causeOfDeath = ''
        self.deathTime = ''
        self.hasVoted = False
    
    def __str__(self):
        #Clean this up after testing
        return f'{self.name} - {self.team} - {self.hasVoted} - {self.isAlive}'

    async def checkPlayerVoted(self):
        return self.hasVoted

    #async def assignTeam(self, teamList, playerList):
    #    team = random.choice(teamList)
    #    teamList.remove(team)
    #    self.team = team
    #    playerList.playerlist.append(self)


class Role:

    def __init__(self, Name = 'Vanilla Townie', Team = 'Town'):
        self.name = Name
        self.team = Team

    def __str__(self):
        return f'{self.name} - {self.team}'


class Vote:

    def __init__(self, Day, Voter, VoteTarget = 'no one'):#, voteTime):
        #Make Voter/VoteTarget Player() class?
        self.voter = Voter
        self.voteTarget = VoteTarget
        self.voteDay = Day
        #self.voteTime = voteTime

    def __str__(self):
        return f'{self.voter} is voting for {self.voteTarget} on Day {self.voteDay}'