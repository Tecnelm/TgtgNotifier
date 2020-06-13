# -*- coding: UTF-8 -*-
import configparser
import tgtg
import json 
import smtplib    ## Importation du 
import unicodedata


parser = configparser.ConfigParser()
parser.read("config.ini")
login = parser.get("TGTG","login")
password = parser.get("TGTG","password")
token = parser.get("TGTG","token")
userid = parser.get("TGTG","userid")
error = tgtg.TgtgLoginError

emailSource = parser.get("Email","source")
passwordSource = parser.get("Email","password")
mailGoal = parser.get("Email","goal")
if (token == "" or token == "None" )or(userid =="" or userid =="None") :
    tgtg = tgtg.TgtgClient(email=login,password=password)
      
else : 
    try:
        tgtg = tgtg.TgtgClient(access_token=token,user_id=userid)
    except (error):
        tgtg = tgtg.TgtgClient(email=login,password=password)


result =tgtg.get_items()
if (token == "" or token == "None" )or(userid =="" or userid =="None") or str(tgtg.access_token) != token or userid != str(tgtg.user_id)  :
    parser.set("TGTG","userid",str(tgtg.user_id))
    parser.set("TGTG","token",str(tgtg.access_token))
    with open("config.ini","w") as config:
        parser.write(config) 
        config.close()
        
for item in result:
    strname = item.get("display_name")
    availableItem = item.get("items_available")
    message = "%s : Il y a %s pannier(s) %s  disponible"%(strname,str(availableItem),strname)    ## Message à envoyer
    
    message = unicodedata.normalize('NFD', message)
    message =message.encode("ascii","ignore")
    message =str(str(message)[2:-1])

    message = """\
            Subject: TGTG notifier



    """+message

    nameconvert = unicodedata.normalize('NFD', strname)
    nameconvert =nameconvert.encode("ascii","ignore")
    nameconvert =str(str(nameconvert)[2:-1].replace(" ","_"))
    try:
        last_state_item = parser.getint("LOG",nameconvert)
    except (configparser.NoSectionError,configparser.NoOptionError):
        parser.set("LOG",nameconvert,str(availableItem))
        last_state_item = 0
        with open("config.ini","w") as config:
            parser.write(config) 
            config.close()

    if(last_state_item == 0  and last_state_item != availableItem):
        
        serveur = smtplib.SMTP('smtp.gmail.com', 587)    ## Connexion au serveur sortant (en précisant son nom et son port)
        serveur.starttls()    ## Spécification de la sécurisation
        serveur.login(emailSource, passwordSource)    ## Authentification
        serveur.sendmail(emailSource, mailGoal, message)    ## Envoie du message
        serveur.quit()    ## Déconnexion du serveur

    if(last_state_item != availableItem):    
        parser.set("LOG",nameconvert,str(availableItem))
        with open("config.ini","w") as config:
            parser.write(config)   
            config.close()