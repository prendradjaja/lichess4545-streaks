import collections

DRAWS_OK = False


streaks = collections.defaultdict(int)
max_streak = (-1, None)

EXCLUDE_PLAYERS = [
    'DracoxVitae',  # presumably cheater
    # 'FelixNL',  # account closed on lichess and slack, not sure if cheater
]

Game = collections.namedtuple('Game', 'decisive winner loser white black date url')

def parse(game):
    for line in game.split('\n'):
        if line.startswith('[White '):
            _, white, _ = line.split('"')
        elif line.startswith('[Black '):
            _, black, _ = line.split('"')
        elif line.startswith('[Result '):
            _, resultstring, _ = line.split('"')
        elif line.startswith('[Date '):
            _, date, _ = line.split('"')
        elif line.startswith('[Site '):
            _, url, _ = line.split('"')
    if resultstring == '1-0':
        return Game(True, white, black, white, black, date, url)
    elif resultstring == '0-1':
        return Game(True, black, white, white, black, date, url)
    elif resultstring == '1/2-1/2':
        return Game(False, None, None, white, black, date, url)
    else:
        1/0

# Might be possible for a player to play two games on the same day and for those games to get reversed by this sort
games = sorted((parse(g) for g in open('modified.pgn').read().strip().split('\n\n\n')),
               key = lambda g: g.date)

def create_test_game(winner, loser):
    result = Game(True, winner, loser, winner, loser, str(create_test_game.i), str(create_test_game.i))
    create_test_game.i += 1
    return result
create_test_game.i = 1

def get_max(player):
    if player not in EXCLUDE_PLAYERS:
        return max(max_streak, (streaks[player], player))
    else:
        return max_streak

for g in games:
    if g.decisive:
        # Loser
        max_streak = get_max(g.loser)
        streaks[g.loser] = 0
        # Winner
        streaks[g.winner] += 1
        max_streak = get_max(g.winner)
    else:
        if DRAWS_OK:
            continue
        else:
            max_streak = get_max(g.white)
            max_streak = get_max(g.black)
            streaks[g.white] = 0
            streaks[g.black] = 0


length, champion = max_streak

print(f'The longest streak (DRAWS_OK={DRAWS_OK}) was {length} games by {champion}')
print('\nWarning: This script does not account for ties -- i.e. if multiple people had a streak\nof this length, only one will be displayed above.')
print('\nYou can change DRAWS_OK by editing streaks.py.')
print('\nHere are all the games that player played in chronological order.')
if not DRAWS_OK:
    print('# means win, . means loss or draw')
else:
    print('## means win, #. means draw, .. means loss')
print()

def other(g, player):
    return g.white if g.white != player else g.black

for g in games:
    if champion in [g.white, g.black]:
        if DRAWS_OK:
            if g.winner == champion:
                symbol = '##'
            elif not g.decisive:
                symbol = '#.'
            else:
                symbol = '..'
        else:
            symbol = '#' if g.winner == champion else '.'
        print(symbol, g.url, 'vs ' + other(g, champion))
