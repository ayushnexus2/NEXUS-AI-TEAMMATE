import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from bot.jobs import JobStore
from bot.switch_adapter import SwitchAdapter, SwitchNotConfigured

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("nexus")

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "").strip()
ALLOWED_CHANNEL_ID = os.getenv("ALLOWED_CHANNEL_ID", "").strip()
MAX_TASK_CHARS = int(os.getenv("MAX_TASK_CHARS", "1500"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
jobs = JobStore()
switch = SwitchAdapter()

def channel_allowed(channel_id: int) -> bool:
    return not ALLOWED_CHANNEL_ID or str(channel_id) == ALLOWED_CHANNEL_ID

@bot.event
async def on_ready():
    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    else:
        await bot.tree.sync()
    log.info("NEXUS logged in as %s", bot.user)

@bot.tree.command(name="health", description="Check whether NEXUS AI TEAMMATE is online.")
async def health(interaction: discord.Interaction):
    await interaction.response.send_message("NEXUS is online. Use `/task` to assign work.", ephemeral=True)

@bot.tree.command(name="task", description="Give a coding task to the NEXUS team agent.")
@app_commands.describe(description="Describe the coding task, expected result, and relevant context.")
async def task(interaction: discord.Interaction, description: str):
    if not channel_allowed(interaction.channel_id):
        await interaction.response.send_message("NEXUS is not enabled in this channel.", ephemeral=True)
        return
    description = description.strip()
    if not description:
        await interaction.response.send_message("Please provide a task description.", ephemeral=True)
        return
    if len(description) > MAX_TASK_CHARS:
        await interaction.response.send_message(f"Task is too long. Limit: {MAX_TASK_CHARS} characters.", ephemeral=True)
        return

    job = jobs.create(description, str(interaction.user), interaction.channel_id)
    await interaction.response.send_message(
        f"🧩 **NEXUS received your task**\n"
        f"**Job:** `{job.id}`\n"
        f"**Status:** `queued`\n"
        f"**Task:** {discord.utils.escape_markdown(description[:700])}"
    )
    channel = interaction.channel
    jobs.update(job.id, status="running")
    try:
        result = await switch.execute(job.id, description)
        jobs.update(job.id, status="completed", result=result)
        await channel.send(f"✅ **NEXUS completed `{job.id}`**\n{result}")
    except SwitchNotConfigured as exc:
        jobs.update(job.id, status="needs_setup", error=str(exc))
        await channel.send(f"⚙️ **NEXUS task `{job.id}` needs setup**\n{exc}")
    except Exception as exc:
        log.exception("Task %s failed", job.id)
        jobs.update(job.id, status="failed", error=str(exc)[:500])
        await channel.send(f"❌ **NEXUS could not complete `{job.id}`**\n`{type(exc).__name__}`: {str(exc)[:700]}")

@bot.tree.command(name="job", description="Check the status of a NEXUS task.")
@app_commands.describe(job_id="The 8-character job ID returned by /task.")
async def job(interaction: discord.Interaction, job_id: str):
    item = jobs.get(job_id.strip())
    if not item:
        await interaction.response.send_message("Job not found. Jobs are stored only while this bot process is running.", ephemeral=True)
        return
    msg = f"**Job `{item.id}`**\nStatus: `{item.status}`\nTask: {item.description[:700]}"
    if item.error:
        msg += f"\nError: {item.error[:500]}"
    if item.result:
        msg += f"\nResult: {item.result[:1200]}"
    await interaction.response.send_message(msg, ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN. Copy .env.example to .env and add your token.")
    bot.run(TOKEN)
