import os
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1470045879145857066
Ip = os.getenv("Ip")  # Minecraft server IP

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=["!", "?"], intents=intents)

# ======================
# HELPERS
# ======================
def get_log_channel(guild: discord.Guild):
    return discord.utils.get(guild.text_channels, name="log")

# ======================
# RULES EMBED
# ======================
def rules_embed():
    embed = discord.Embed(
        title="📜 Welcome to the Server!",
        description="Please read the rules carefully ❤️",
        color=discord.Color.red()
    )

    embed.add_field(
        name="💬 Discord Rules",
        value=(
            "🤝 Be respectful to everyone\n"
            "🚫 No spamming or excessive tagging\n"
            "🔞 No NSFW or disturbing content\n"
            "📢 No advertising without staff permission\n"
            "⚠️ No illegal activity\n"
            "🔐 Do not share personal information\n"
            "🧭 Use the correct channels\n"
            "👮 Staff decisions are final"
        ),
        inline=False
    )

    embed.set_footer(text="⚠️ Breaking rules may result in punishment")
    return embed

# ======================
# READY
# ======================
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user}")

# ======================
# MEMBER JOIN
# ======================
@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != GUILD_ID:
        return
    try:
        await member.send(embed=rules_embed())
    except discord.Forbidden:
        pass

# ======================
# SEND RULES
# ======================
@bot.tree.command(name="send", description="Send rules")
async def slash_send(interaction: discord.Interaction):
    await interaction.response.send_message(embed=rules_embed())

@bot.command()
async def send(ctx):
    await ctx.send(embed=rules_embed())

# ==================================================
# 🌍 IP COMMAND (?ip and !ip)
# ==================================================
@bot.command(name="ip")
async def ip(ctx):
    if not Ip:
        await ctx.send("❌ Server IP is not set.")
        return

    embed = discord.Embed(
        title="🌍 Minecraft Server IP",
        description=f"```{Ip}```",
        color=discord.Color.green()
    )
    embed.set_footer(text="Copy & paste into Minecraft")

    await ctx.send(embed=embed)

# ==================================================
# 🔨 MODERATION COMMANDS
# ==================================================

# ===== KICK =====
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"👢 **Kicked** {member.mention}\n📄 Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don’t have permission to kick this user.")

# ===== ROLE ADD / REMOVE =====
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, action: str, member: discord.Member, role: discord.Role):
    if ctx.guild.id != GUILD_ID:
        return

    try:
        if action.lower() == "add":
            await member.add_roles(role)
            await ctx.send(f"🏷️ Added {role.mention} to {member.mention}")

        elif action.lower() == "remove":
            await member.remove_roles(role)
            await ctx.send(f"🏷️ Removed {role.mention} from {member.mention}")

        else:
            await ctx.send("❌ Usage: `?role add @user @role` or `?role remove @user @role`")

    except discord.Forbidden:
        await ctx.send("❌ I can’t manage that role (role hierarchy issue).")

# ===== PURGE =====
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send("❌ You must delete at least 1 message.")
        return

    if amount > 100:
        await ctx.send("❌ You can only delete up to 100 messages at once.")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)

    log_channel = get_log_channel(ctx.guild)
    if log_channel:
        await log_channel.send(
            f"🧹 **Messages Purged**\n"
            f"👤 Moderator: {ctx.author.mention}\n"
            f"📍 Channel: {ctx.channel.mention}\n"
            f"🗑️ Amount: {len(deleted) - 1}"
        )

# ==================================================
# 📋 LOGGING EVENTS
# ==================================================

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.guild.id != GUILD_ID:
        return

    log_channel = get_log_channel(after.guild)
    if not log_channel:
        return

    before_roles = set(before.roles)
    after_roles = set(after.roles)

    for role in after_roles - before_roles:
        await log_channel.send(
            f"➕ **Role Added**\n👤 User: {after.mention}\n🏷️ Role: {role.mention}"
        )

    for role in before_roles - after_roles:
        await log_channel.send(
            f"➖ **Role Removed**\n👤 User: {after.mention}\n🏷️ Role: {role.mention}"
        )

@bot.event
async def on_message_delete(message: discord.Message):
    if not message.guild or message.guild.id != GUILD_ID:
        return
    if message.author.bot:
        return

    log_channel = get_log_channel(message.guild)
    if not log_channel:
        return

    await log_channel.send(
        f"🗑️ **Message Deleted**\n"
        f"👤 Author: {message.author.mention}\n"
        f"📍 Channel: {message.channel.mention}\n"
        f"💬 Content:\n```{message.content or 'No text content'}```"
    )

# ======================
# START BOT
# ======================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)
