import discord
from discord.ext import commands
from os import getenv
from cah import Game


description = '''A bot for managing games of Kings.'''

bot = commands.Bot(command_prefix='!', description=description)

games = {}


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')
    await bot.change_presence(activity=discord.Game(name='CaH'))


@bot.command()
async def playing(ctx):
    '''
    Checks if there is a game in the current channel.
    '''
    if ctx.channel in games:
        await ctx.send('There is a game in this channel!  Say !join to join.')
    else:
        await ctx.send('There is no game in this channel. Say !start to start one!')


@bot.command()
async def players(ctx):
    '''
    Display the players in this game.
    '''

    if ctx.channel in games:
        game = games[ctx.channel]
        await ctx.send(embed= discord.Embed(
            title="Players",
            description=','.join(f'<@{i.id}>' for i in game.players)
        ))
    else:
        await ctx.send('There is no game in this channel. Say !start to start one!')


@bot.command()
async def start(ctx):
    '''
    Starts a game of kings in this channel.
    '''
    if ctx.channel in games:
        await ctx.send('There is already a game of CaH in this channel.')
    else:
        game = Game()
        games[ctx.channel] = game
        game.add_player(ctx.author.id)
        await ctx.send(f'{ctx.author} has started a game of CaH')


@bot.command()
async def end(ctx):
    '''
    Ends the game of kings in the current channel.
    '''
    if ctx.channel in games:
        del games[ctx.channel]
        await ctx.send('Game Over. You could always !start another one.')
    else:
        await ctx.send('No game in this channel.')


@bot.command()
async def join(ctx):
    '''
    Join the game in this channel.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        if not any(i.id == ctx.author.id for i in game.players):
            game.add_player(ctx.author.id)
            await ctx.send(f'{ctx.author.name} has joined the game of CaH.')
        else:
            await ctx.send("You have already joined the game")


@bot.command()
async def quit(ctx):
    '''
    Leave the game in this channel.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        player = next((i for i in game.players if i.id == ctx.author.id), None)
        if player:
            print(player.id)
            game.players.remove(player)
        else:
            await ctx.send("You are not part of the game")

            if not game.players:
                del games[ctx.channel]
        await ctx.send(f'{ctx.author.name} has left the game of CaH')




@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command")
    else:
        raise error

if __name__ == '__main__':
    bot.run(getenv('token'))

"""
@bot.command()
async def shuffle(ctx):
    '''
    Shuffles all cards back into the deck, emptying hands.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        await game.deck.reset()
        await game.deck.shuffle()
        for player in game.players:
            player.hand = set()
        await ctx.send('Everything is back in the pile.')


@bot.command()
async def hand(ctx):
    '''
    DMs your hand to you
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        if ctx.author in game.players:
            player = await game.get_player(ctx.author)
            message = '\n'.join(
                player.hand) if player.hand else 'You have an empty hand'
            await ctx.author.send(message)


@bot.command()
async def deal(ctx):
    '''
    Deals a card to the player.
    '''
    if ctx.channel not in games:
        return
    game = games[ctx.channel]
    tup = await game.draw()
    if not tup:
        await ctx.send('That was the last card!  Feel free to !start over...')
    else:
        player, card = tup
        await ctx.send('{} you drew the {}'.format(player.mention, card))
        if card.value in game.rules:
            await ctx.send('{}: {}'.format(card.value, game.rules[card.value]))

@bot.command()
async def kick(ctx, player: discord.Member):
    '''
    Remove a player from the game
    '''
    player = next((i for i in games[ctx.channel].players if i.id == ctx.author.id), None)
    if ctx.channel in games and player:
        games[ctx.channel].players.remove(player)
        await ctx.send(f"{ctx.author.name} was removed from the game")


@bot.command()
async def count(ctx):
    '''
    Display the number of remaining cards
    '''
    await ctx.send("Thare are {} cards remaining.".format(len(games[ctx.channel].deck)))


@bot.command()
async def addplayer(ctx, player: discord.User):
    '''
    Add a person to the game.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        if not any(i.id == ctx.author.id for i in game.players):
            game.add_player(ctx.author.id)
            await ctx.send(f"{ctx.author.name} was added to the game")
        else:
            await ctx.send("You're already playing {}".format(player.mention))

"""