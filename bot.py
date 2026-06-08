import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté : {bot.user}")


@bot.tree.command(name="createsalons", description="Crée plusieurs salons et renomme le serveur")
@app_commands.describe(
    nom="Nom des salons à créer",
    nombre="Combien de salons créer (max 500)",
    nom_serveur="Nouveau nom du serveur",
    categorie_id="ID de la catégorie (optionnel)"
)
@app_commands.checks.has_permissions(manage_channels=True, manage_guild=True)
async def createsalons(
    interaction: discord.Interaction,
    nom: str,
    nombre: int,
    nom_serveur: str,
    categorie_id: str = None
):

    # limite sécurité
    if nombre < 1 or nombre > 500:
        await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 500.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"⏳ Renommage du serveur + création de **{nombre}** salons...",
        ephemeral=True
    )

    guild = interaction.guild

    # 🔥 Renommer le serveur
    try:
        await guild.edit(name=nom_serveur)
    except discord.Forbidden:
        await interaction.edit_original_response(
            content="❌ Je n'ai pas la permission de renommer le serveur."
        )
        return

    # Catégorie optionnelle
    categorie = None
    if categorie_id:
        categorie = guild.get_channel(int(categorie_id))
        if not isinstance(categorie, discord.CategoryChannel):
            categorie = None

    crees = 0
    erreurs = 0

    # Création des salons + @everyone
    for i in range(nombre):
        try:
            channel = await guild.create_text_channel(
                name=nom,
                category=categorie
            )
            crees += 1

            # 🔥 mention @everyone dans chaque salon
            try:
                await channel.send("@everyone")
            except discord.Forbidden:
                pass  # pas la permission de mentionner

            # anti rate limit
            if crees % 10 == 0:
                await asyncio.sleep(1.5)

        except discord.Forbidden:
            erreurs += 1
            break

        except discord.HTTPException:
            erreurs += 1
            await asyncio.sleep(2)

    msg = f"✅ **{crees}** salons créés avec `{nom}`"
    msg += f"\n🏷️ Serveur renommé en `{nom_serveur}`"

    if erreurs:
        msg += f"\n❌ **{erreurs}** erreurs"

    await interaction.edit_original_response(content=msg)


@createsalons.error
async def createsalons_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Tu n'as pas les permissions nécessaires (**Gérer les salons + serveur**).",
            ephemeral=True
        )

bot.run(TOKEN)
