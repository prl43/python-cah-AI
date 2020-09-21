import discord
from discord.ext import commands
from os import getenv
from cah import Game
from itertools import cycle
from asyncio import sleep
import random

description = '''A bot for playing games of CaH.'''

bot = commands.Bot(command_prefix='!', description=description)

games = {}
player2channel = {}


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
        await ctx.send(f'There is a game in this channel!  Say {bot.command_prefix}join to join.')
    else:
        await ctx.send(f'There is no game in this channel. Say {bot.command_prefix}create to create one!')


@bot.command()
async def players(ctx):
    '''
    Display the players in this game.
    '''

    if ctx.channel in games:
        game = games[ctx.channel]
        await ctx.send(embed=discord.Embed(
            title="Players",
            description=','.join(f'<@{i.id}>' for i in game.players)
        ))
    else:
        await ctx.send(f'There is no game in this channel. Say {bot.command_prefix}create to create one!')


@bot.command()
@commands.guild_only()
async def create(ctx):
    '''
    Creates a of CaH in this channel.
    '''
    if ctx.channel in games:
        await ctx.send('There is already a game of CaH in this channel.')
    else:
        game = Game()
        game.host = ctx.author.id
        games[ctx.channel] = game
        player = game.add_player(ctx.author.id)
        game.set_card_tzar(player)
        player2channel[ctx.author.id] = ctx.channel
        await ctx.send(f'{ctx.author} has created a game of CaH')


@bot.command()
@commands.guild_only()
async def start(ctx):
    '''
    Starts the game of CaH in this channel. (Host-only)
    '''
    if ctx.channel not in games:
        return await ctx.send("There are no CaH games in this channel")
    game = games[ctx.channel]
    if ctx.author.id != game.host:
        return await ctx.send("Only the Host may start the game")
    game.deal_cards()
    game.next_tzar = cycle(game.players)
    next(game.next_tzar)
    await ctx.send(embed=discord.Embed(
        description=f"{ctx.author.name} has started the game of CaH\n<@{game.card_tzar.id}> is the Tzar this round"
    ))
    cmd = bot.get_command(name='deal')
    await ctx.invoke(cmd)


@bot.command()
@commands.guild_only()
async def deal(ctx):
    '''
    Deal the cards, called automatically (todo: hide)
    '''
    if ctx.channel not in games:
        return await ctx.send("There are no CaH games in this channel")
    game = games[ctx.channel]
    game.deal_cards()
    # hide players actual id
    fake_id = [i for i in range(1, len(game.players) + 1)]
    random.shuffle(fake_id)
    i = 0
    for player in game.players:
        player.fake_id = fake_id[i]
        i += 1

    _, q = game.get_new_question()
    await ctx.send(embed=discord.Embed(title="Question",
                                       description=q))

    for player in game.players:
        if player == game.card_tzar:
            continue
        cards = player.cards
        user = bot.get_user(player.id)
        cards = list(cards.values())
        cards = enumerate(cards, start=1)
        show = ""
        show = [show + f"{i}) {j}\n" for i, j in cards]
        show = ''.join(show)

        await user.send(embed=discord.Embed(
            title="Your cards are",
            description=show
        ))


@bot.command()
@commands.guild_only()
async def end(ctx):
    '''
    Ends the game of CaH in the current channel.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        if game.host == ctx.author.id:
            del games[ctx.channel]
            await ctx.send(f' Host has ended the game. You can use {bot.command_prefix}start another one.')
        else:
            await ctx.send("Only host may end the game")
    else:
        await ctx.send('No game in this channel.')


@bot.command()
@commands.guild_only()
async def join(ctx):
    '''
    Join the game in this channel.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        if not any(i.id == ctx.author.id for i in game.players):
            game.add_player(ctx.author.id)
            player2channel[ctx.author.id] = ctx.channel
            await ctx.send(f'{ctx.author.name} has joined the game of CaH.')
        else:
            await ctx.send("You have already joined the game")


@bot.command()
@commands.dm_only()
async def select(ctx, num: int):
    '''
    Pick a card among the ones you have as the answer to the question
    '''
    if ctx.author.id not in player2channel:
        return await ctx.send("You're not part of a game!")

    cur_channel = player2channel[ctx.author.id]
    game = games[cur_channel]
    if game.card_tzar.id == ctx.author.id:
        return await ctx.send("Tzar has to judge cards this round")

    if num > 8:
        return await ctx.send("You must pick one among the 8 cards you have")
    player = next((i for i in game.players if i.id == ctx.author.id), None)
    if not player:
        return await ctx.send("You're not currently playing a game of CaH")
    if player.fake_id in game.has_played:
        return await ctx.send("You have already chosen a card")
    card = game.set_player_card(player, list(player.cards.keys())[num - 1])
    game.player_choices.append(card)
    tzar = bot.get_user(game.card_tzar.id)
    await tzar.send(embed=discord.Embed(title=f"Player {player.fake_id} chose:",
                                        description=card))
    game.finish_round += 1
    game.has_played.append(player.fake_id)
    if game.finish_round == len(game.players) - 1:
        choices = enumerate(game.player_choices, start=1)
        _, q = game.curr_question
        choice = discord.Embed(title="Cards chosen were", description=q)
        for i, c in choices:
            choice.add_field(name=str(i), value=c)
        await cur_channel.send(embed=choice)


@bot.command()
@commands.guild_only()
async def cards(ctx):
    '''
    Shows the currently selcted cards
    '''
    if ctx.channel not in games:
        return await ctx.send(f"There is no ongoing game in this channel\nUse {bot.command_prefix}create to create one")
    game = games[ctx.channel]
    if ctx.author.id != game.card_tzar.id:
        return await ctx.send("Only the Tzar may show the current selection")
    if game.player_choices == []:
        return await ctx.send("No choices were made this round (yet)")
    choices = enumerate(game.player_choices, start=1)
    _, q = game.curr_question
    choice = discord.Embed(title="Cards chosen were", description=q)
    for i, c in choices:
        choice.add_field(name=str(i), value=c)
    await ctx.channel.send(embed=choice)


@bot.command()
@commands.guild_only()
async def choose(ctx, fake_id: int):
    '''
    (Tzar only) pick a card as that rounds winner
    '''
    cur_channel = player2channel[ctx.author.id]
    game = games[cur_channel]
    print(game.has_played)
    if game.card_tzar.id != ctx.author.id:
        await ctx.send("Only the Tzar may choose the winner")

    player = next((i for i in game.players if i.fake_id == fake_id), None)
    if not player:
        return await ctx.send(
            f"You must select someone playing the game\nDo {bot.command_prefix}players to see the list")
    if player.fake_id not in game.has_played:
        return await ctx.send("Player didn't select a card during this round")
    if player.id == game.card_tzar.id:
        return await ctx.send("Tzar may not select themselves")

    game.set_round_winner(player)
    _, card = game.player_cards[player]
    _, q = game.curr_question
    await ctx.send(embed=discord.Embed(
        description=f"<@{player.id}> won the round\nQuestion: {q}\nAnswer: {card}"
    ))
    await sleep(2)
    cmd = bot.get_command(name='score')
    await ctx.invoke(cmd)
    game.cur_round += 1
    # check if win:
    if player.wins == game.win_pts:
        del games[ctx.channel]
        return await ctx.send(embed=discord.Embed(
            title="Game Over!",
            description=f"<@{player.id}> has won the game",
        ).set_footer(text=f"Round: {game.cur_round}/{game.max_round}"))
    elif game.cur_round > game.max_round:
        score_board = {player.id: player.wins for player in players}
        score_board = {k: v for k, v in sorted(score_board.items(), key=lambda item: item[1])}
        plr, pt = next(iter(score_board.items()))
        del games[ctx.channel]
        return await ctx.send(embed=discord.Embed(
            title=f"Game Over",
            description=f"<@{plr}> wins with {pt} points"
        ))

    game.card_tzar = next(game.next_tzar)
    game.finish_round = 0
    game.player_choices = []
    game.has_played = []
    await sleep(2)
    await ctx.send(f"The Tzar has chosen\n<@{game.card_tzar.id}> is the new Tzar")
    await sleep(8)
    cmd = bot.get_command(name='deal')
    await ctx.invoke(cmd)


@bot.command()
@commands.guild_only()
async def quit(ctx):
    '''
    Leave the game in this channel.
    '''
    if ctx.channel in games:
        game = games[ctx.channel]
        player = next((i for i in game.players if i.id == ctx.author.id), None)
        if player:
            game.players.remove(player)
            del player2channel[ctx.author.id]

        else:
            await ctx.send("You are not part of the game")

            if not game.players:
                del games[ctx.channel]
        await ctx.send(f'{ctx.author.name} has left the game of CaH')


@bot.command()
async def score(ctx):
    '''
    Shows the scoreboard for the game in this channel
    '''
    if ctx.channel not in games:
        return await ctx.send("No game in this channel.")
    game = games[ctx.channel]
    players = game.players
    score_board = {player.id: player.wins for player in players}
    score_board = {k: v for k, v in sorted(score_board.items(), key=lambda item: item[1])}
    print(score_board)
    board = [f'<@{p}> : {s}\n' for p, s in score_board.items()]
    board = ''.join(board)
    await ctx.send(embed=discord.Embed(
        title="Scoreboard",
        description=board
    ).set_footer(text=f"Round: {game.cur_round}/{game.max_round}"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        raise error


if __name__ == '__main__':
    bot.run(getenv('token1'))
