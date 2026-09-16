import asyncio
import json
import os

import discord
from discord import app_commands

TOKEN_PLACEHOLDER = "PON_AQUI_TU_TOKEN_DEL_BOT"

ROLES = [
    {"key": "fabri", "name": "👑 Fabri", "color": 0xFFD700, "hoist": True, "mentionable": False, "locked": True},
    {"key": "admin", "name": "🛡️ Admin", "color": 0xE74C3C, "hoist": True, "mentionable": True, "locked": True},
    {"key": "mod", "name": "🛡️ Mod", "color": 0x2ECC71, "hoist": True, "mentionable": True, "locked": True},
    {"key": "gamer", "name": "🎮 Gamer", "color": 0x3498DB, "hoist": True, "mentionable": True, "locked": False},
    {"key": "seguidor", "name": "👥 Seguidor", "color": 0x9B59B6, "hoist": False, "mentionable": True, "locked": False},
]

CATEGORIES = {
    "📋 INFORMACIÓN": [
        ("📜-reglas", discord.ChannelType.text),
        ("📢-anuncios", discord.ChannelType.text),
    ],
    "📢 COMUNICACIÓN": [
        ("💬-general", discord.ChannelType.text),
        ("🔊-general-voz", discord.ChannelType.voice),
    ],
    "🎬 CONTENIDO": [
        ("🎮-clips", discord.ChannelType.text),
        ("🔴-streams", discord.ChannelType.text),
        ("🎥-vods", discord.ChannelType.text),
        ("📀-videos", discord.ChannelType.text),
    ],
    "🖼️ MEDIA": [
        ("✨-multimedia", discord.ChannelType.text),
        ("😂-memes", discord.ChannelType.text),
    ],
}

RULES_EMBED = discord.Embed(
    title="📜 Reglas de la comunidad",
    description=(
        "1. 🙏 Respeto ante todo, cero hate.\n"
        "2. 🚫 Nada de spam ni contenido ofensivo.\n"
        "3. 🇪🇸 El idioma principal es español.\n"
        "4. 🎭 Pedí tus roles con /roles.\n"
        "5. ✨ Divertite y cuidá la comunidad!"
    ),
    color=0xE74C3C,
)


def load_config():
    try:
        with open("config.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


config = load_config()
TOKEN = os.environ.get("DISCORD_TOKEN") or config.get("token")
if not TOKEN or TOKEN == TOKEN_PLACEHOLDER:
    raise SystemExit(
        "Configura tu token: variable de entorno DISCORD_TOKEN o config.json"
    )

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class RoleButton(discord.ui.Button):
    def __init__(self, role_def: dict):
        super().__init__(
            label=role_def["name"],
            style=discord.ButtonStyle.primary,
            custom_id=f"role_{role_def['key']}",
        )
        self.role_key = role_def["key"]

    async def callback(self, interaction: discord.Interaction):
        role_def = next((r for r in ROLES if r["key"] == self.role_key), None)
        if not role_def:
            return
        if role_def["locked"]:
            await interaction.response.send_message(
                f"{role_def['name']} no puede asignarse con botones (es administrativo).",
                ephemeral=True,
            )
            return
        role = discord.utils.get(interaction.guild.roles, name=role_def["name"])
        if not role:
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Quitaste el rol {role_def['name']}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Obtuviste el rol {role_def['name']}", ephemeral=True)


class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for r in ROLES:
            if not r["locked"]:
                self.add_item(RoleButton(r))

    @discord.ui.button(label="📜 Reglas", style=discord.ButtonStyle.secondary, custom_id="open_rules", row=1)
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=RULES_EMBED, ephemeral=True)


class SetupBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(RoleView())
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content.strip() in ("!setup", "!configurar"):
            if message.author.id == message.guild.owner_id or message.author.guild_permissions.administrator:
                await self.run_setup(message.guild, message.channel, source="message")
            else:
                await message.channel.send("❌ Solo el dueño del servidor puede usar este comando.")
        elif message.content.startswith("!roles"):
            await self.send_role_panel(message.channel)

    async def on_interaction(self, interaction: discord.Interaction):
        # Fallback para botones persistentes tras reinicios
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id", "")
            if custom_id == "open_rules":
                await interaction.response.send_message(embed=RULES_EMBED, ephemeral=True)
            elif custom_id.startswith("role_"):
                await self._toggle_role(interaction, custom_id.replace("role_", ""))

    async def _toggle_role(self, interaction: discord.Interaction, key: str):
        role_def = next((r for r in ROLES if r["key"] == key), None)
        if not role_def:
            return
        role = discord.utils.get(interaction.guild.roles, name=role_def["name"])
        if not role:
            return
        if role_def["locked"]:
            await interaction.response.send_message(
                f"{role_def['name']} no puede asignarse con botones (es administrativo).",
                ephemeral=True,
            )
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Quitaste el rol {role_def['name']}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Obtuviste el rol {role_def['name']}", ephemeral=True)

    async def run_setup(self, guild: discord.Guild, target, source="slash"):
        created_roles = 0
        created_channels = 0

        try:
            for r in ROLES:
                if not discord.utils.get(guild.roles, name=r["name"]):
                    await guild.create_role(
                        name=r["name"],
                        color=r["color"],
                        hoist=r["hoist"],
                        mentionable=r["mentionable"],
                    )
                    created_roles += 1

            for cat_name, channels in CATEGORIES.items():
                category = discord.utils.get(guild.categories, name=cat_name)
                if not category:
                    category = await guild.create_category(cat_name)
                    created_channels += 1

                for ch_name, ch_type in channels:
                    if ch_type == discord.ChannelType.voice:
                        if not discord.utils.get(category.voice_channels, name=ch_name):
                            await guild.create_voice_channel(ch_name, category=category)
                            created_channels += 1
                    else:
                        if not discord.utils.get(category.text_channels, name=ch_name):
                            await guild.create_text_channel(ch_name, category=category)
                            created_channels += 1

            general = discord.utils.get(guild.text_channels, name="💬-general")
            if general:
                anuncios = discord.utils.get(guild.text_channels, name="📢-anuncios")
                embed = discord.Embed(
                    title="🏡 ¡Bienvenido al servidor!",
                    description=(
                        "Este es el hub de la comunidad.\n\n"
                        "**Cómo empezar:**\n"
                        f"1. Pasate por <#{anuncios.id if anuncios else general.id}> para enterarte de las novedades\n"
                        "2. Elegí tus roles en el panel de abajo\n"
                        "3. Divertite en los canales 🎮\n\n"
                        "**Comandos:**\n"
                        "- `/roles` — panel de roles\n"
                        "- `/setup` — (dueño) crea/actualiza roles y canales"
                    ),
                    color=0xFFD700,
                )
                view = RoleView()
                already = False
                async for msg in general.history(limit=20):
                    if msg.author == self.user and msg.embeds and "Bienvenido" in (msg.embeds[0].title or ""):
                        already = True
                        break
                if not already:
                    await general.send(embed=embed, view=view)

            summary = (
                "✅ **Servidor configurado.**\n\n"
                "**Roles:** 👑 Fabri, 🛡️ Admin, 🛡️ Mod, 🎮 Gamer, 👥 Seguidor\n"
                "**Categorías:** 📋 Información, 📢 Comunicación, 🎬 Contenido, 🖼️ Media\n"
                "**Canales:** Reglas, Anuncios, General, Clips, Streams, VODs, Videos, Multimedia, Memes y Voz.\n\n"
                f"Creados: {created_roles} roles, {created_channels} canales\n"
                "💡 Mensaje de bienvenida enviado en #💬-general"
            )
            if source == "slash":
                await target.edit_original_response(content=summary)
            else:
                await target.send(summary)
            print(f"✅ Setup completado en {guild.name}")
        except Exception as e:
            err = f"❌ Error al configurar: {e}"
            if source == "slash":
                await target.edit_original_response(content=err)
            else:
                await target.send(err)
            print(err)

    async def send_role_panel(self, channel, interaction=None):
        embed = discord.Embed(
            title="🎭 Roles de la comunidad",
            description=(
                "Clic en un rol para obtenerlo. Clic de nuevo para quitarlo.\n\n"
                "**Administrativos:** 👑 Fabri, 🛡️ Admin, 🛡️ Mod (asignados por el staff)"
            ),
            color=0x3498DB,
        )
        view = RoleView()
        if interaction:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await channel.send(embed=embed, view=view)


bot = SetupBot()


@bot.tree.command(name="setup", description="Crea/actualiza roles y canales del servidor")
@app_commands.default_permissions(administrator=True)
async def setup_slash(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Solo el dueño del servidor puede usar este comando.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await bot.run_setup(interaction.guild, interaction, source="slash")


@bot.tree.command(name="roles", description="Panel interactivo de roles")
async def roles_slash(interaction: discord.Interaction):
    await bot.send_role_panel(interaction.channel, interaction=interaction)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())