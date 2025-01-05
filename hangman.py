import os
import random
import customtkinter as gui
from tkinter import *
from tkinter.font import Font

# enable brainrot words
brainrot = True

# load fonts
gui.FontManager.load_font(os.path.join("Poppins-SemiBold.ttf"))
gui.FontManager.load_font(os.path.join("Roboto-Regular.ttf"))
# set text styles
displaytext = ("Poppins", 32)
normaltext = ("Roboto", 16)
titletext = ("Roboto", 24) 
# gui window
window = gui.CTk()
# window title
window.title("Hangman")

# clear the window
def clear():
    # for every widget in the window
    for widget in window.winfo_children():
        # eject them
        widget.destroy()

# create label
def label(text : str, style : tuple, row : int, column : int, columnspan=None):
    if columnspan:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10)
    else:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column, padx=10, pady=10)

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

# prompt for game parameters
def gameconfig():
    # clear the window
    clear()
    # create and place title label
    label("Welcome to Hangman", titletext, 1, 1, columnspan=2)
    # number of players
    gui.CTkOptionMenu(window, ["singleplayer", "multiplayer"], "singleplayer")
    # parameter labels


"""
MAIN THREAD
"""
# ask for initial parameters
gameconfig()
# start window
window.mainloop()