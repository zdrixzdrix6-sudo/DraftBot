import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté : {bot.user}")


# =========================
# CREATE SALONS COMMAND
# =========================
@bot.tree.command(
    name="createsalons",
    description="Crée des salons et des rôles sans rien supprimer"
)
@app_commands.describe(
    nom="Nom des salons",
    nombre="Nombre de salons (max 500)",
    nom_serveur="Nouveau nom du serveur",
    nom_role="Nom des rôles",
    categorie_id="ID de la catégorie (optionnel)"
)
@app_commands.checks.has_permissions(
    manage_channels=True,
    manage_roles=True,
    manage_guild=True
)
async def createsalons(
    interaction: discord.Interaction,
    nom: str,
    nombre: int,
    nom_serveur: str,
    nom_role: str,
    categorie_id: str = None
):

    if nombre < 1 or nombre > 500:
        await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 500.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "⏳ Création en cours...",
        ephemeral=True
    )

    guild = interaction.guild

    # Renommer le serveur
    try:
        await guild.edit(name=nom_serveur)
    except discord.Forbidden:
        pass

    # Créer les rôles
    try:
        for i in range(5):
            await guild.create_role(name=f"{nom_role}-{i + 1}")
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur création rôles : {e}"
        )
        return

    # Catégorie optionnelle
    categorie = None
    if categorie_id:
        try:
            categorie = guild.get_channel(int(categorie_id))
        except:
            pass

    # Création des salons
    semaphore = asyncio.Semaphore(10)

    async def create_channel(i):
        async with semaphore:
            channel = await guild.create_text_channel(
                name=f"{nom}-{i + 1}",
                category=categorie
            )
            try:
                await channel.send("@everyone")
            except:
                pass

    await asyncio.gather(
        *[create_channel(i) for i in range(nombre)],
        return_exceptions=True
    )

    await interaction.edit_original_response(
        content=(
            f"✅ Terminé !\n"
            f"📌 Serveur renommé : {nom_serveur}\n"
            f"📌 Salons créés : {nombre}\n"
            f"📌 Rôles créés : 5"
        )
    )


# =========================
# DELETE ALL CHANNELS COMMAND
# =========================
@bot.tree.command(
    name="delete_all_channels",
    description="Supprime tous les salons du serveur (sans confirmation)"
)
@app_commands.checks.has_permissions(manage_channels=True)
async def delete_all_channels(interaction: discord.Interaction):

    guild = interaction.guild

    await interaction.response.send_message(
        "🧨 Suppression de tous les salons en cours...",
        ephemeral=True
    )

    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.2)
        except:
            pass

    await interaction.followup.send(
        "✅ Tous les salons ont été supprimés.",
        ephemeral=True
    )


# =========================
# ERROR HANDLER
# =========================
@createsalons.error
async def createsalons_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Permissions insuffisantes.",
            ephemeral=True
        )


bot.run(TOKEN)
