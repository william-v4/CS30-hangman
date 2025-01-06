from math import floor
import os
import random
import re
from time import sleep
import customtkinter as gui
from tkinter import *
from transformers import pipeline
import torch
import warnings

# enable brainrot words
brainrot = True

# suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, message="CTkLabel Warning: Given image is not CTkImage")
warnings.filterwarnings("ignore", category=UserWarning, message="CTkButton Warning: Given image is not CTkImage")
# load fonts
gui.FontManager.load_font(os.path.join("Poppins-SemiBold.ttf"))
gui.FontManager.load_font(os.path.join("Roboto-Regular.ttf"))
# set text styles
displaytext = ("Poppins SemiBold", 32)
normaltext = ("Roboto", 16)
titletext = ("Roboto", 24) 
# gui window
window = gui.CTk()
# window title
window.title("Hangman")
# game mode
gamemode = StringVar(window)
# default is singleplayer
gamemode.set("singleplayer")
# guessed letters and words
guessed = []
# wrong guesses
wrong = []


# clear the window
def clear():
    # for every widget in the window
    for widget in window.winfo_children():
        # eject them
        widget.destroy()

# create label (warning: labels created with this cannot be referenced later)
def label(text : str, style : tuple, row : int, column : int, columnspan=None):
    if columnspan:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10,)
    else:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column, padx=10, pady=10)

# sanitize words and phrases
def sanitize(input : str) -> str:
    # store output
    output = ""
    # only add letters and spaces (removing anything else)
    # for every character in input
    for char in input:
        # if the character is an alphabetical character or a space
        if char.isalpha() or char.isspace():
            # add it to the output
            output += char
    # convert to lowercase return the output
    return output.lower()

# prompt for game parameters
def gameconfig():
    # global variables
    global gamemode, enablephrases
    # clear the window
    clear()
    # clear guesslists
    guessed.clear()
    wrong.clear()
    # create and place title label
    label("Welcome to Hangman", displaytext, 1, 2, columnspan=3)
    # ask for game mode with dropdown menu. default is singleplayer. when changed, call multiplayerconfig() to decide whether to ask for custom word
    gui.CTkOptionMenu(window, values=["singleplayer", "multiplayer"], variable=gamemode, font=normaltext, command=multiplayerconfig).grid(row=2, column=2, columnspan=3, padx=10, pady=10)
    if gamemode.get() == "singleplayer":
        # if singleplayer, ask wheter to enable phrases
        label("enable phrases?", normaltext, 3, 1, columnspan=2)
        # store switch state
        enablephrases = IntVar(window)
        # switch for phrases
        gui.CTkSwitch(window, variable=enablephrases, text="").grid(row=3, column=3, columnspan=1, padx=0, pady=10)
    # button to start the game, runs startgame() when clicked
    gui.CTkButton(window, text="start game", font=normaltext, command=startgame).grid(row=5, column=2, columnspan=3, padx=10, pady=10)

# custom word for multiplayer
def multiplayerconfig(arg=None):
    # global variables
    global customword, customwordprompt
    # if multiplayer
    if gamemode.get() == "multiplayer":
        # reset config window
        gameconfig()
        # store custom word
        customword = StringVar(window)
        # ask for word
        customwordprompt = gui.CTkLabel(window, text="what's your word?", font=normaltext)
        customwordprompt.grid(row=3, column=2, columnspan=3, padx=10, pady=10)
        # text field for word. when changed, stores contents in customword
        gui.CTkEntry(window, font=normaltext, textvariable=customword).grid(row=4, column=2, columnspan=3, padx=10, pady=10)
    # otherwise, reset the config window for singleplayer and add aditional config options
    else:
        gameconfig()

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

# get phrase from local LLM
def LLMphrase() -> str:
    print("getting phrase from Llama-3.2-3B-Instruct")
    # configure HuggingFace pipeline
    llm = pipeline(
        # task
        "text-generation",
        # llama 3B because 8B killed my computer
        model="meta-llama/Llama-3.2-3B-Instruct",
        # additional parameters outlined in model card
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    # prompts
    messages = [
        {
            "role": "system", 
            "content": "You are part of a game of Hangman, providing a short phrase for the participant to guess. Your response must be in the form of a short English phrase. The phrase must be a common phrase, expression, or idiom and must be a single independent clause. Do not use any punctuation. Do not use contractions. Do not use apostrophes, commas, or periods. Only put a single space between words. The response must be in the form of an all-lowercase short phrase. Respond with the phrase and nothing else. Do not respond with the prompt. Only respond with the phrase once. The independent clause must be shorter than 5 words and be complete. The phrase must no include dependent clauses. The phrase must be easy to guess."
        }, 
        {"role": "user", "content": "Generate the phrase."}
    ]
    # generated output. 10 tokens should be enough. random temperature for better variety
    outputs = llm(messages, max_new_tokens=10, temperature=random.uniform(0.3, 0.9))
    # return just the generated phrase (see `llama example output structure.js` for output structure)
    return outputs[0]["generated_text"][-1]['content']

# read config and start game
def startgame(arg=None):
    # global variables
    global answer, boardstate, guesses, worddisplay, guesscounter, guessfield, guessentry, wrongdisplay, maxguesses
    # clear the window
    clear()
    # if multiplayer
    if gamemode.get() == "multiplayer":
        # get custom word and sanitize it
        answer = sanitize(customword.get())
    # otherwise, it is singleplayer
    else:
        # if phrases are enabled and random chance 1/10
        if enablephrases.get() and random.randint(1, 10) == random.randint(1, 10):
            # try to get phrase from LLM
            try:
                answer = sanitize(LLMphrase())
            # if failed, get a random phrase from list
            except:
                print("failed to get phrase from LLM")
                # same process as in getword()
                answer = random.choice(open("contemporaryphrases.txt", "r").readlines()).replace("\n", "").replace(" ", "").lower()
        # otherwise, get a random word
        else:
            answer = getword()
    # set total guesses to the length of answer, but not more than half the alphabet
    guesses = min(len(answer), 13)
    maxguesses = guesses
    # generate game board state, which is an underscore for every letter in the word and spaces for every space
    boardstate = ""
    # for every character in the answer
    for char in answer:
        # if it is a space, add a dash
        if char == " ":
            boardstate += "-"
        # otherwise, add an underscore
        else:
            boardstate += "_"
    # place word display
    worddisplay = gui.CTkLabel(window, text="", font=displaytext)
    worddisplay.grid(row=1, column=2, columnspan=2, padx=10, pady=10)
    # prompt for guess
    label("make a guess", normaltext, 2, 1, columnspan=2)
    # store guess
    guessentry = StringVar(window)
    # guess input field
    guessfield = gui.CTkEntry(window, font=normaltext, textvariable=guessentry)
    guessfield.grid(row=3, column=1, padx=10, pady=10)
    # bind enter key to guess()
    window.bind("<Return>", guess)
    # show guesses left
    guesscounter = gui.CTkLabel(window, text=str(guesses), font=displaytext)
    guesscounter.grid(row=3, column=2, padx=10, pady=10)
    # wrong guesses display
    wrongdisplay = gui.CTkLabel(window, text="", font=normaltext)
    wrongdisplay.grid(row=4, column=1, columnspan=2, padx=10, pady=10)
    # update game board
    updateboard()

# update the game board
def updateboard():
    # global variables
    global boardstate, worddisplay, guesses, guesscounter, wrongdisplay
    # clear the word display
    worddisplay.configure(text="")
    # store the new word display text
    newtext = ""
    # for every character in the board state
    for char in boardstate:
        # add it to new word display text followed by a space
        newtext += (char + " ")
    # set the word display text to the new text
    worddisplay.configure(text=newtext)
    # update guess counter
    guesscounter.configure(text=str(guesses))
    # store wrong guesses output
    wrongoutput = ""
    # for every wrong guess
    for guess in wrong:
        # add it to the wrong guesses output followed by a ", "
        wrongoutput += (guess + ", ")
    # update the display
    wrongdisplay.configure(text=wrongoutput)
    # available graphics
    abductpics = ["abduct1.png", "abduct2.png", "abduct3.png", "abduct4.png", "abduct5.png"]
    # frame to display graphic
    graphicframe = gui.CTkLabel(window, text="")
    graphicframe.grid(row=1, column=1, padx=10, pady=10)
    # first, check if guesses are less than 0
    if guesses <= 0:
        # set graphic to the last one
        graphicframe.configure(image=PhotoImage(file=abductpics[-1]))
    # otherwise, show appropriate graphic based on guesses left
    else:
        graphicframe.configure(image=PhotoImage(file=abductpics[
            # max index of abductpics * ratio of guesses left to max guesses, rounded down
            floor((len(abductpics) - 1) * (maxguesses - guesses) / maxguesses)
        ]))
    # update window
    window.update()
    # debug
    # print(answer)
    # print(boardstate)

# clear guess input field
def CE():
    global guessentry
    guessentry.set("")

# make a guess
def guess(arg=None):
    # global variables
    global boardstate, guesses, answer, guessentry
    # get the guess from the entry field
    entry = sanitize(guessentry.get())
    # if guess is empty or whitespace, clear the entry field and return
    if entry == "" or entry.isspace(): 
        CE()
        return
    # if the guess is already in the guessed list
    if entry in guessed:
        # clear the entry field and return
        CE()
        return
    # if the guess is a single letter (not including spaces)
    if len(entry.replace(" ", "")) == 1:
        # if the guess is in the word, the guess is correct
        if entry in answer:
            # iterator
            index = 0
            # for every character in the word
            for char in answer:
                # if the character is the guess
                if char == entry:
                    # replace the character in the board state with the guess
                    #   initial    characters before   guess    characters after
                    boardstate = boardstate[:index] + entry + boardstate[index + 1:]
                # onto the next letter
                index += 1
        # if not, the guess is wrong
        else:
            # decrement the guesses
            guesses -= 1
            # add the guess to wrong guesses
            wrong.append(entry)
    # otherwise, if the guess is a word (more than one letter)
    elif len(entry) > 1:
        # find the positions of the guess in the answer
        matches = list(re.finditer(r'\b' + re.escape(entry) + r'\b', answer))
        # if there are matches
        if matches:
            # for every match
            for match in matches:
                # note start and end index
                start_index = match.start()
                end_index = match.end()
                # update the boardstate with the correct guessed word (same process as in single letter guess)
                boardstate = boardstate[:start_index] + entry + boardstate[end_index:]
        # if not, the guess is wrong
        else:
            # decrement the guesses (2 for a wrong word)
            guesses -= 2
            # add the guess to wrong guesses
            wrong.append(entry)
    # regardless of validity, add the guess to the guessed list
    guessed.append(entry)
    # clear the entry field
    CE()
    # update the game board
    updateboard()
    # check if the player has lost
    if guesses <= 0:
         # disable entry
        guessfield.configure(state=DISABLED)
        # show the end screen
        endscreen("the answer was " + answer)
    # if the board state (with spaces instead of dashes) is the same as the answer
    if boardstate.replace("-", " ") == answer:
        # the player has won
        # disable entry
        guessfield.configure(state=DISABLED)
        # wait a bit for player to admire their victory
        sleep(2)
        # show the end screen
        endscreen("you escaped unscathed")

# game end screen
def endscreen(message : str):
    # clear window
    clear()
    # show message
    label(message, displaytext, 1, 2, columnspan=3)
    # button to restart the game
    gui.CTkButton(window, text="", command=gameconfig, image=PhotoImage(file="restart.png")).grid(row=2, column=2, columnspan=3, padx=10, pady=10)
    # reset default dropdown value
    global gamemode
    gamemode.set("singleplayer")

"""
MAIN THREAD
"""
# ask for initial parameters
gameconfig()
# start window
window.mainloop()
