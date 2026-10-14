import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()
quiz_en_cours = False
currentindex = 0
# Stockage des gains de la journée : {user_id: {"nom": nom, "wl": total_wl, "weed": total_weed}}
gains_journee = {}
# Mettez ici l'identifiant du salon #quizz (juste les chiffres, sans guillemets)
SALON_ID = 1549347659763159070

# Vos questions, réponses et gains
QUESTIONS = [
   
   

    {
        "question": "Quel est le nom de la chaîne de montagnes qui sépare l'Europe de l'Asie ?",
        "reponse": "L'Oural",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le symbole chimique du carbone ?",
        "reponse": "C",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le pays d'origine du compositeur Wolfgang Amadeus Mozart ?",
        "reponse": "L'Autriche",
        "gain": "1000 wl !"
    },
    {
        "question": "Quelle est la plus grande île du monde ?",
        "reponse": "Le Groenland",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom du célèbre détective créé par Agatha Christie ?",
        "reponse": "Hercule Poirot",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le gaz principal rejeté par les volcans lors d'une éruption ?",
        "reponse": "La vapeur d'eau",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom du héros de la saga vidéoludique 'The Legend of Zelda' ?",
        "reponse": "Link",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le plus ancien des sept merveilles du monde antique encore debout ?",
        "reponse": "La Grande Pyramide de Gizeh",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le pays dont la forme rappelle celle d'une botte ?",
        "reponse": "L'Italie",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le nom de la force qui attire les corps vers le centre de la Terre ?",
        "reponse": "La gravité",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le prénom du célèbre détective Holmes ?",
        "reponse": "Sherlock",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le plus grand ravin du monde, situé aux États-Unis ?",
        "reponse": "Le Grand Canyon",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom scientifique de la vitamine C ?",
        "reponse": "L'acide ascorbique",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le premier élément du tableau périodique ?",
        "reponse": "L'hydrogène",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom de l'actrice principale du film Titanic ?",
        "reponse": "Kate Winslet",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le pays qui possède le plus de volcans actifs au monde ?",
        "reponse": "L'Indonésie",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom de la monnaie unique européenne ?",
        "reponse": "L'euro",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le plus grand papillon du monde ?",
        "reponse": "L'Attacus atlas",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le compositeur de l'opéra 'Carmen' ?",
        "reponse": "Georges Bizet",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le nom du volcan qui a détruit Pompéi ?",
        "reponse": "Le Vésuve",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le pays d'origine du jeu d'échecs moderne ?",
        "reponse": "L'Inde",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le nom de la plus haute montagne d'Afrique ?",
        "reponse": "Le Kilimandjaro",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le symbole chimique de l'azote ?",
        "reponse": "N",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est l'auteur du roman '1984' ?",
        "reponse": "George Orwell",
        "gain": "150 gr de weed ! "
    },
    {
        "question": "Quel est le nom de la particule élémentaire porteuse d'une charge négative ?",
        "reponse": "L'électron",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le plus grand État du monde en superficie ?",
        "reponse": "La Russie",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le nom de la célèbre tour penchée en Italie ?",
        "reponse": "La tour de Pise",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le nom du fleuve qui traverse Paris ?",
        "reponse": "La Seine",
        "gain": "150 gr de weed !"
    },
    {
        "question": "Quel est le sport individuel le plus pratiqué au monde ?",
        "reponse": "La course à pied",
        "gain": "1000 wl !"
    },
    {
        "question": "Quel est le nom de la célèbre créature du loch Ness ?",
        "reponse": "Nessie",
        "gain": "150 gr de weed !  "
    }
]



currentindex = 0

def ajouter_gain_utilisateur(user, gain_texte):
    # On extrait la valeur numérique et le type de gain (wl ou weed)
    # Ex de gain_texte : "1000 wl !" ou "150 gr de weed !"
    parts = gain_texte.split()
    montant = int(parts[0])
    type_gain = "weed" if "weed" in gain_texte.lower() else "wl"

    user_id = user.id
    if user_id not in gains_journee:
        gains_journee[user_id] = {"nom": user.display_name, "wl": 0, "weed": 0}

    # On cumule selon le type
    if type_gain == "wl":
        gains_journee[user_id]["wl"] += montant
    else:

        gains_journee[user_id]["weed"] += montant
        
async def poser_question():
    global currentindex, quiz_en_cours
    
    # 1. On vérifie d'abord si le salon existe
    salon = bot.get_channel(SALON_ID)
    if not salon:
        return

    # 2. On vérifie si un quiz est déjà en cours
    if quiz_en_cours:
        return
        
    # On active le verrou
    quiz_en_cours = True

    try:
        q_actuelle = QUESTIONS[currentindex]

        # On protège l'envoi de la question contre le Rate Limit
        try:
            await salon.send(f"🚨 *QUESTION DU QUIZ !* 🚨\n\n{q_actuelle['question']}\n*(Répondez directement dans ce salon !)*")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la question : {e}")
            quiz_en_cours = False
            return

        def check(m):
            if m.channel.id != SALON_ID or m.author.bot:
                return False
            reponse_utilisateur = m.content.strip().lower()
            reponse_vraie = q_actuelle["reponse"].strip().lower()
            return reponse_vraie in reponse_utilisateur or reponse_utilisateur in reponse_vraie

        try:
            message_gagnant = await bot.wait_for('message', timeout=600.0, check=check)
            gagnant = message_gagnant.author
            gain = q_actuelle["gain"]

            # ---- AJOUT ICI : On mémorise et cumule le gain du gagnant ----
            ajouter_gain_utilisateur(gagnant, gain)

            await salon.send(f"🎉 *Bravo {gagnant.mention} !* C'était bien : *{q_actuelle['reponse']}\n🏆 Tu remportes : *{gain}** !")
            
            currentindex += 1
            if currentindex >= len(QUESTIONS):
                currentindex = 0

        except asyncio.TimeoutError:
            await salon.send(f"⏱️ *Temps écoulé !* Personne n'a trouvé la bonne réponse.\n💡 La bonne réponse était : *{q_actuelle['reponse']}*")
            currentindex += 1
            if currentindex >= len(QUESTIONS):
                currentindex = 0

    finally:
        # Sécurité ultime : dans TOUS les cas (succès, timeout ou erreur), 
        # on libère le verrou pour que le quiz suivant puisse se lancer.
        quiz_en_cours = False

    
@tasks.loop(minutes=1)
async def verifier_horraires():
    try:
        
        maintenant = datetime.now(ZoneInfo("Europe/Paris"))
        print(f"Vérification de l'heure : {maintenant.hour}h{maintenant.minute}")
        
        heures_quiz = [(10, 0), (11, 30), (13, 0), (14, 30), (16, 0), (17, 30), (19, 0), (20, 30), (22, 0)]
        
        if (maintenant.hour, maintenant.minute) in heures_quiz:
            if not quiz_en_cours:
                await poser_question()
                
                # ---> AJOUT ICI : Si c'était la session de 22h, on envoie le récap après le quiz <---
                if maintenant.hour == 22 and maintenant.minute == 0:
                    salon = bot.get_channel(SALON_ID)
                    if salon and gains_journee:
                        embed = discord.Embed(
                            title="🏆 Récapitulatif de la journée 👑",
                            color=discord.Color.gold(),
                            timestamp=datetime.now(),
                        )
                        texte_recap = ""
                        for data in gains_journee.values():
                            texte_recap += f"• *{data['nom']}* a gagné *{data['wl']} wl* et *{data['weed']} gr de weed* 👑\n"
                        
                        embed.description = texte_recap
                        await salon.send(embed=embed)
                        gains_journee.clear() # Remise à zéro pour le lendemain !
            else:
                print("Un quiz est déjà en cours, report de la question.")
                
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("Attention : Rate limit (429) détecté, pause de sécurité activée.")
            await asyncio.sleep(60)
        else:
            print(f"Erreur HTTP rencontrée : {e}")

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name}")
    if not verifier_horraires.is_running():
        verifier_horraires.start()

bot.run(os.getenv('DISCORD_TOKEN'))