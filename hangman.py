import random
from time import sleep

brainrot = True

# get random word randomly either from common or brainrot words file
def getword() -> str:
    # if brainrot is enabled, add brainrot words as well as common words to the word list
    if brainrot:
        wordlist = open("commonwords.txt", "r").readlines() + open("brainrot.txt", "r").readlines()
    # otherwise, just use the common words
    else:
        wordlist = open("commonwords.txt", "r").readlines()
    # get a random word from the word list, strip it of whitespace and newline characters, make it lowercase, and return it
    return random.choice(wordlist).replace("\n", "").replace(" ", "").lower()

while True:
    print(getword())
    sleep(1)