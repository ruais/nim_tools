### Nim tools by Lynn (ruais)

from typing import Tuple, Union

def alpha_index(n: Union[int, str]) -> Union[str, int]:
    '''
    Convert between numerical indexing and 'Excel x-axis'-style indexing.
    
    Microsoft Excel uses alphabetical indexing for its x-axis. This begins with
    A through Z, followed by AA, AB, AC, ..., AZ, BA, BB, ... .
    Assuming 'A' -> 0, convert between this notation and numerical indexes.
    
    Keyword arguments:
    n -- the number to convert from: int for numerical, str for Excel-style
    
    Functions:
    alphalen -- return the length of the output string based on the int input
    floorval -- return the lowest index of a string of this length
    
    Examples:
    >>> alpha_index('AYL')
    1337
    >>> alpha_index(214441)
    'LEET'
    '''
    from math import log
    numalpha = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    alphalen = lambda i: int(log(25*i+26, 26))
    floorval = lambda length: int((26**length-26)/25)
    if type(n) is int:
        strlen = alphalen(n)
        n -= floorval(strlen)
        upper = []
        while len(upper) < strlen:
            n, rem = divmod(n, 26)
            upper.append(numalpha[10:][rem])
        return ''.join(upper[::-1])
    else:
        lower = floorval(len(n))
        upper = ''
        for c in n.upper():
            upper += numalpha[numalpha[10:].index(c)]
        return lower + int(upper, 26)

def nimwin(piles: Tuple[int, ...], misere: bool = False) -> Tuple[int, tuple]:
    '''
    Calculate the possible moves to have control in a game of Nim.
    
    Keyword arguments:
    piles  -- a tuple of ints: each represents an amount of tokens in a pile
    misere -- gamemode:
                  False if the aim is to take the last token
                  True if the aim is to leave one token for the opponent
                  (default False)
    
    Returns:
    sub  -- the positive int of tokens to remove from a pile to keep control
    opts -- a tuple of ints: each is the index of a pile $sub can be subbed from
        if there is no move to take control (sub == 0), $opts returns empty
    
    Examples:
    -- $misere will not affect scenarios until endgame is reached
    >>> nimwin((4, 2, 1))
    (1, (0,))
    >>> nimwin((4, 2, 1), misere = True)
    (1, (0,))
    >>> nimwin((6, 6, 2, 1))
    (1, (0, 1, 2))
    >>> nimwin((6, 6, 2, 1), misere = True)
    (1, (0, 1, 2))
    >>> nimwin((2, 2))
    (0, ())
    >>> nimwin((2, 2), misere = True)
    (0, ())
    
    -- during endgame, $misere corrects $sub for changed win condition
    >>> nimwin((1, 2, 1))
    (2, (1,))
    >>> nimwin((1, 2, 1), misere = True)
    (1, (1,))
    >>> nimwin((1, 1))
    (0, ())
    >>> nimwin((1, 1), misere = True)
    (1, (0, 1))
    '''
    from functools import reduce
    
    # endgame is reached when all future moves remove the last token in a pile
    endgame = sum(1 for p in piles if p > 1) <= 1
    misere = misere and endgame
    if misere and sum(1 for p in piles if p > 0) % 2:
        misere = -1
    
    sub = reduce(lambda i, j: i ^ j, piles)
    
    opts = []
    if sub + misere:
        abjunct = sub
        for i, p in enumerate(piles):
            # match = sub NIMPLY p
            match = sub & ~p
            if match < abjunct:
                abjunct = match
                opts = []
            if match == abjunct:
                opts.append(i)
        
        sub -= 2 * abjunct
    
    sub += misere
    opts = tuple(opts)
    
    return sub, opts

def nimgen(seed: int = None, fairstart: bool = True) -> Tuple[list, int]:
    '''
    Generate a seeded starting position for a game of Nim.
    
    Keyword arguments:
    seed      -- seed used for replicable generation
                     (default None)
    fairstart -- whether the first player can gain control during their turn
                     (default True)
    
    See also:
    nimwin -- calculate possible moves to gain control in a game of Nim
    
    Returns:
    piles -- a list of ints: each represents an amount of tokens in a pile
    seed  -- the seed used during the generation of this starting position
    
    Examples:
    >>> nimgen()
    ([5, 8, 9, 7, 2, 8], 8563507259942795255)
    >>> nimgen()
    ([2, 2, 10, 6, 6], 3290797037641845650)
    >>> nimgen(3290797037641845650)
    ([2, 2, 10, 6, 6], 3290797037641845650)
    '''
    import random, sys
    
    # arbitrarily chosen values; cause some short games and some long games
    minpiles  = 3
    maxpiles  = 7
    mintokens = 2
    maxtokens = 12
    
    if seed is None:
        seed = random.randrange(sys.maxsize)
    
    random.seed(seed)
    piles = random.randint(minpiles, maxpiles-1) * [0]
    
    for i in range(len(piles)):
        piles[i] = random.randint(mintokens, maxtokens)
    
    winnable, stack = nimwin(piles)
    # create another pile to (un)balance the game (match $fairstart)
    if fairstart != bool(winnable):
        selector = stack or range(len(piles))
        selector = random.choice(selector)
        
        newpile = piles[selector] - winnable
        newpile ^= piles[selector]
        
        piles.append(newpile or random.randint(mintokens, maxtokens))
    
    return piles, seed

def nimvisualise(piles: Tuple[int, ...]):
    '''
    Print a visualisation of token piles in Nim.
    
    Keyword arguments:
    piles -- a tuple of ints: each represents an amount of tokens in a pile
    
    See also:
    alpha_index -- convert between numerical and alphabetical indices
    
    Examples:
    >>> nimvisualise((2, 4, 1))
    4   X  
    3   X  
    2 X X  
    1 X X X
      A B C
    '''
    highest = len(str(max(piles)))
    indices = [alpha_index(i) for i in range(len(piles))]
    spacing = len(indices[-1])
    pad = lambda s, p = spacing: (p-len(s)) * ' ' + s
    for i in range(max(piles), 0, -1):
        print(pad(str(i), highest), end=' ')
        print(*(map(pad, ['X' if p >= i else '' for p in piles])))
    print(pad('', highest), *(map(pad, indices)))

def nimplay(seed: Union[int, tuple] = None, misere: bool = False,
            fairstart: bool = True, humanstart: bool = True) -> None:
    '''
    Run a game of Nim against a basic CPU opponent.
    
    Generate a game of Nim, and maintain that game to its completion. Control a
    CPU opponent which will always make the best move. If the CPU cannot take
    control, it will take a randomised amount of tokens from any available pile
    (up to (total/2 + 1)).
    
    The game ends when the last token is taken, or when the human player inputs
    '-end'. Moves are made by typing the chosen pile and the amount to remove.
    All tokens in a pile can be taken with the commandword '-all'.
    
    Keyword arguments:
    seed       -- seed used for replicable generation
                      (default None)
    misere     -- gamemode:
                      False if the aim is to take the last token
                      True if the aim is to leave one token for the opponent
                      (default False)
    fairstart  -- whether the first player can gain control during their turn
                      (default True)
    humanstart -- whether the human is the first player
                      (default True)
    
    Examples:
    >>> nimplay()
    game: 2300488424522623117 - [10, 6, 4]
    
    10 X    
     9 X    
     8 X    
     7 X    
     6 X X  
     5 X X  
     4 X X X
     3 X X X
     2 X X X
     1 X X X
       A B C
    
    ----
    
    you: a -8
    
    6   X  
    5   X  
    4   X X
    3   X X
    2 X X X
    1 X X X
      A B C
    
    ----
    
    cpu: C -1
    
    6   X  
    5   X  
    4   X  
    3   X X
    2 X X X
    1 X X X
      A B C
    
    ----
    
    you: b -5
    
    3     X
    2 X   X
    1 X X X
      A B C
    
    ----
    
    cpu: A -1
    
    3     X
    2     X
    1 X X X
      A B C
    
    ----
    
    you: c -all
    
    1 X X  
      A B C
    
    ----
    
    cpu: B -1
    
    1 X    
      A B C
    
    ----
    
    you: a -1
    
    you win!
    '''
    import random, re
    
    if type(seed) is tuple:
        piles = list(seed)
        seed = 'custom'
    else:
        piles, seed = nimgen(seed, fairstart)
    
    print(f'game: {seed} - {piles}\n')
    
    yourturn = humanstart
    # resets the seed: ensures that even when replaying the same game, cpu will
    # make different mistakes
    random.seed()
    
    while any(p for p in piles):
        nimvisualise(piles)
        print('\n----\n')
        print(end = f"{('cpu', 'you')[yourturn]}: ")
        
        if yourturn:
            while yourturn:
                parse = re.findall('-(END)|([A-Z]+)|(-ALL|[0-9]+)|.',
                                    input().upper())
                comm = []
                pile = []
                remv = []
                comp = (comm, pile, remv)
                for part in parse:
                    for i in range(3):
                        if part[i]: comp[i].append(part[i])
                
                if sum(map(len, comp)) == 1 and comm:
                    if comm[0] == 'END':
                        return
                if len(pile) == 1 == len(remv) > len(comm):
                    pile = alpha_index(pile[0])
                    
                    if remv[0] == '-ALL':
                        remv = piles[pile]
                    else:
                        remv = int(remv[0])
                    
                    if pile < len(piles) and piles[pile] >= remv > 0:
                        yourturn = False
                
                print(end=('\n', '     ')[yourturn])
        else:
            remv, pile = nimwin(piles, misere)
            if not pile:
                pile = [i for i, p in enumerate(piles) if p > 0]
            pile = random.choice(pile)
            if not remv:
                remv = random.randint(1, int(piles[pile]/2) + 1)
            
            print(f'{alpha_index(pile)} -{remv}\n')
            yourturn = True
        
        piles[pile] -= remv
    
    print(f"you {('win', 'lose')[yourturn ^ misere]}!")
