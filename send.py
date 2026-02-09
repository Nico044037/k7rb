import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

# ======================
# ENV
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")
Ip = os.getenv("Ip", "")
GUILD_ID = 1470045879145857066

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=["?", "!"], intents=intents)

# ======================
# HELPERS
# ======================
def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name="log")

def rules_embed():
    embed = discord.Embed(
        title="📜 Welcome to the Server!",
        description="Please read the rules carefully ❤️",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Rules",
        value=(
            "🤝 Be respectful\n"
            "🚫 No spam\n"
            "🔞 No NSFW\n"
            "📢 No ads\n"
            "⚠️ No illegal activity\n"
            "🔐 No personal info\n"
            "👮 Staff decisions are final"
        ),
        inline=False
    )
    return embed

# ======================
# READY
# ======================
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}")

# ======================
# BASIC TEST COMMAND
# ======================
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Prefix commands work.")

# ======================
# SEND RULES
# ======================
@bot.command()
async def send(ctx):
    await ctx.send(embed=rules_embed())

# ======================
# IP COMMAND
# ======================
@bot.command()
async def ip(ctx):
    if not Ip:
        await ctx.send("❌ Server IP not set.")
        return

    embed = discord.Embed(
        title="🌍 Server IP",
        description=f"```{Ip}```",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# ======================
# SERVER INFO
# ======================
@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    humans = sum(not m.bot for m in g.members)
    bots = sum(m.bot for m in g.members)

    embed = discord.Embed(
        title=f"ℹ️ {g.name}",
        color=discord.Color.blurple(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=g.icon.url if g.icon else None)

    embed.add_field(name="Owner", value=g.owner.mention if g.owner else "Unknown")
    embed.add_field(name="Members", value=g.member_count)
    embed.add_field(name="Humans", value=humans)
    embed.add_field(name="Bots", value=bots)
    embed.add_field(name="Channels", value=len(g.channels))
    embed.add_field(name="Roles", value=len(g.roles))
    embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"))

    await ctx.send(embed=embed)

# ======================
# MODERATION
# ======================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member.mention}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, action, member: discord.Member, role: discord.Role):
    if action.lower() == "add":
        await member.add_roles(role)
        await ctx.send(f"➕ Added {role.mention} to {member.mention}")
    elif action.lower() == "remove":
        await member.remove_roles(role)
        await ctx.send(f"➖ Removed {role.mention} from {member.mention}")
    else:
        await ctx.send("Usage: `?role add @user @role`")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("❌ 1–100 only")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)

    log = get_log_channel(ctx.guild)
    if log:
        await log.send(
            f"🧹 Purged {len(deleted)-1} messages in {ctx.channel.mention}\n"
            f"Moderator: {ctx.author.mention}"
        )

# ======================
# LOGGING
# ======================
@bot.event
async def on_member_update(before, after):
    log = get_log_channel(after.guild)
    if not log:
        return

    for r in set(after.roles) - set(before.roles):
        await log.send(f"➕ {after.mention} got {r.mention}")
    for r in set(before.roles) - set(after.roles):
        await log.send(f"➖ {after.mention} lost {r.mention}")

@bot.event
async def on_message_delete(msg):
    if not msg.guild or msg.author.bot:
        return

    log = get_log_channel(msg.guild)
    if log:
        await log.send(
            f"🗑️ Message deleted in {msg.channel.mention}\n"
            f"Author: {msg.author}\n"
            f"```{msg.content or 'No content'}```"
        )

# ======================
# RUN
# ======================
bot.run(TOKEN)
