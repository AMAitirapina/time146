import json
import sys
import os
import subprocess as sp

def learn():
    try:
        memory = open('memory.json', 'r')
    except FileNotFoundError:
        memory = open('memory.json', 'w')
        memory.write('[["Persiste!"], {"Conhecimento": "Conhecimento é sempre bom!", "Tchau": "Tchau! Tchau!"}]')
        memory.close()
        memory = open('memory.json', 'r')
    phrases = json.load(memory)

learn()