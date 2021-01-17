import json
import sys
import os
import subprocess as sp

class Association():
    def __init__(self):
        try:
            memory = open('memory.json', 'r')
        except FileNotFoundError:
            memory = open('memory.json', 'w')
            memory.write('[["Persiste"], {"Conhecimento": "Conhecimento é sempre bom!", "tchau": "Tchau! Tchau!"}]')
            memory.close()
            memory = open('memory.json', 'r')
        self.phrases = json.load(memory)
        memory.close()
        self.historic = [None]

    def listen(self, phrase=None):
        if phrase == None:
            phrase = input('>: ')
        phrase = str(phrase)
        return phrase
    
    def think(self, phrase):
        if phrase in self.phrases:
            return self.phrases[phrase]
        if phrase == 'Forms':
            return "https://docs.google.com/forms/d/e/1FAIpQLSdmrdGbOZgiK6GyStj9HTBBXIji4AycF6o2ZDjsmG9udgSP2w/viewform"
        # learning
        if phrase == 'Aprende':
            return 'O que você quer que eu aprenda?'    
        lastPhrase = self.historic[-1]
        if lastPhrase == 'O que você quer que eu aprenda?':
            self.key = phrase
            return 'Digite o que eu devo responder:'
        if lastPhrase == 'Digite o que eu devo responder:':
            response = phrase
            self.phrases[self.key] = response
            self.saveMemory()
            return 'Aprendido!'
        try:
            response = str(eval(phrase))
            return response
        except:
            pass
        return 'Não entendi...'

    def saveMemory(self):
        memory = open('memory.json', 'w')
        json.dump([self.phrases], memory)
        memory.close()
    
    # open URLs in the search engine
    def speak(self, phrase):
        if 'Executa ' in phrase:
            platform = sys.platform
            command = phrase.replace('Executa ', '')
            if 'win' in platform:
                os.startfile(command)
            if 'linux' in platform:
                try:
                    sp.Popen(command)
                except FileNotFoundError:
                    sp.Popen(['xdg-open', command])
        else:
            print(phrase)
        self.historic.append(phrase)
