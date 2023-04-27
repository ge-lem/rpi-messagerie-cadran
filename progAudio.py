import RPi.GPIO as GPIO
import time
from time import sleep
import os
import subprocess

GPIO.setmode(GPIO.BOARD)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PROJECTDIR="/home/pi/rpi-messagerie-cadran"

TIMEMAXREC = 60

TIMESONNERIE = 60

def decrocher():
    return GPIO.input(23)==0
def raccrocher():
    return GPIO.input(23)!=0


def sonnerie():
    p = subprocess.Popen(["/usr/bin/aplay","sonnette.wav"], cwd=PROJECTDIR)

#Joue un fichier, appel bloquant mais s'arrête si on raccroche ou on commence à composer un numéro
def play_audio(filename):
    p = subprocess.Popen(["/usr/bin/aplay",filename], cwd=PROJECTDIR)
    while(decrocher() and p.poll() is None and GPIO.input(24)):
        sleep(0.1)
    if(p.poll() is None):
        p.terminate()
    return p




def play_intro():
    play_audio("intro.wav")

def play_menu():
    play_audio("menu.wav")

#Décale les fichiers son, le 1 est le dernier son enregistré
def roundfile():
    for i in reversed(range(1,9)):
        if(os.path.isfile(str(i)+".wav")):
            os.replace(str(i)+".wav",str(i+1)+".wav")
    os.replace("recA.wav","1.wav")


sonnerie()

while(True):
    lastsonnette = time.time()
    #Attente que l'on décroche mais sonnerie toute les TIMESONNERIE secondes
    while(raccrocher()):
        if(time.time()-lastsonnette>TIMESONNERIE):
            lastsonnette=time.time()
            sonnerie()
        sleep(0.1)
    sleep(1)
    play_intro()
	
	#Tant qu'on ne raccroche pas
    while(decrocher()):
        play_menu()
        num=0
        while(num==0 and decrocher()):
            while(GPIO.input(24) and decrocher()):
                sleep(0.1)
            print("debut num")
            timeTick=time.time()
            tick_l=GPIO.input(26)
            #On compte le nombre d'impulsions
            while(time.time()-timeTick < 0.5):
                tick = GPIO.input(26)
                if(tick!=tick_l):
                    tick_l=tick
                    timeTick=time.time()
                    sleep(0.01)
                    if(tick):
                        num=num+1
        print("Num composé: "+str(num))
		
		#10 impulsions correspond au numéro 0 donc à l'enregistrement
        if(num==10):
            play_audio("recins.wav")
            if(decrocher()):
            	#On enregistre
                p = subprocess.Popen(["/usr/bin/arecord","-fS16_LE", "-c2", "-r44100" ,"rec.wav"], cwd=PROJECTDIR)
                timestart=time.time()
                while decrocher() and time.time()-timestart<TIMEMAXREC:
                    sleep(0.1)
                p.terminate()
                if(time.time()-timestart>=TIMEMAXREC):
                    play_audio("finrec.wav")
                sleep(1)
            	#On amplifie
                p = subprocess.Popen(["/usr/bin/sox","rec.wav", "recA.wav", "gain", "-n"], cwd=PROJECTDIR)
                p.wait()
                roundfile()
        elif(num > 0):
            sfn=str(num)+".wav"
            if(os.path.isfile(sfn)):
                play_audio(sfn)
        sleep(2)
            
quit()

