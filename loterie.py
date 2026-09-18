import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo
import random
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration modifiable
SALON_LOTERIE_ID = 1549363867019247686
MIN_NUMERO = 1
MAX_NUMERO = 30
GAIN_DEPART = 2000  # Somme de base

# Cagnotte actuelle (commence à 2000 wl)
cagnotte_actuelle = GAIN_DEPART 

# Stockage temporaire des participations : {user_id: {"user": member, "numero": choix}}
participations = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Vérifier si on est dans le bon salon de loterie
    if message.channel.id == SALON_LOTERIE_ID:
        # Chercher tous les nombres dans le message (ex: "17 pour moi" -> trouve "17")
        nombres_trouves = re.findall(r'\d+', message.content)
        
        if nombres_trouves:
            # On prend le premier nombre trouvé dans la phrase
            numero = int(nombres_trouves[0])
            
            if MIN_NUMERO <= numero <= MAX_NUMERO:
                user_id = message.author.id
                
                if user_id in participations:
                    await message.channel.send(f"⚠️ {message.author.mention}, tu as déjà choisi le numéro {participations[user_id]['numero']} pour cette semaine !", delete_after=5)
                else:
                    participations[user_id] = {"user": message.author, "numero": numero}
                    await message.add_reaction("✅")
            else:
                await message.delete()
                await message.channel.send(f"❌ {message.author.mention}, choisis un nombre entre {MIN_NUMERO} et {MAX_NUMERO} !", delete_after=5)
        else:
            # S'il n'y a aucun nombre du tout dans le message, on ignore
            pass

    await bot.process_commands(message)

# Tâche planifiée : Tous les samedis à 20:00
@tasks.loop(minutes=1)
async def tirer_loterie():
    now = datetime.now(ZoneInfo("Europe/Paris"))
    
    # Samedi = 5, à 20h00
    if now.weekday() == 5 and now.hour == 20 and now.minute == 0:
        salon = bot.get_channel(SALON_LOTERIE_ID)
        if not salon:
            return

        if not participations:
            await salon.send("🎟️ Tirage de la Loterie : Aucune participation enregistrée cette semaine !")
            return

        # Tirage au sort du nombre gagnant
        nombre_gagnant = random.randint(MIN_NUMERO, MAX_NUMERO)
        
        # Rechercher les gagnants qui ont trouvé ce numéro
        gagnants = [p["user"] for p in participations.values() if p["numero"] == nombre_gagnant]

        await salon.send(f"🎲 RÉSULTAT DE LA LOTERIE 🎲\nLe numéro tiré au sort est le : {nombre_gagnant} !")

        if gagnants:
            # Mentionner le ou les gagnants et annoncer leur gain en wl
            gagnants_mentions = ", ".join([g.mention for g in gagnants])
            await salon.send(f"🎉 Bravo {gagnants_mentions} ! Tu remportes {cagnotte_actuelle} wl !")
            # Remise à zéro de la cagnotte après un gain
            cagnotte_actuelle = GAIN_DEPART
        else:
            await salon.send("😢 Personne n'a trouvé le bon numéro cette semaine ! Remise en jeu la semaine prochaine.")
            # Augmentation de la cagnotte si pas de gagnant
            cagnotte_actuelle += GAIN_DEPART
            await salon.send(f"💰 Le jackpot augmente ! La cagnotte passe à {cagnotte_actuelle} wl pour la semaine prochaine.")

        # Réinitialisation pour la semaine suivante
        participations.clear()

# L'heure du token de ton bot
bot.run(os.getenv("DISCORD_TOKEN"))