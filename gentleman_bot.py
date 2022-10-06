import asyncio
import logging
from os import path, getenv, makedirs

import discord
from discord import FFmpegOpusAudio
from discord.ext import commands

BOT_TOKEN = getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="~", intents=intents)

storage_dir = path.join(
    getenv("XDG_DATA_HOME", path.expanduser("~/.local/share")), "gentleman-bot"
)


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def info(ctx):
    if ctx.message.mentions:
        theme_path = path.join(
            storage_dir, str(ctx.guild.id), str(ctx.message.mentions[0].id)
        )
    else:
        theme_path = path.join(storage_dir, str(ctx.guild.id), "global")

    if path.isfile(theme_path):
        await ctx.reply("Theme setted")
    else:
        await ctx.reply("No theme setted")


@bot.command()
async def theme(ctx, attachment: discord.Attachment):
    # TODO: validate attachment

    if ctx.message.mentions:
        theme_path = path.join(
            storage_dir, str(ctx.guild.id), str(ctx.message.mentions[0].id)
        )
    else:
        theme_path = path.join(storage_dir, str(ctx.guild.id), "global")

    makedirs(path.dirname(theme_path), exist_ok=True)
    await attachment.save(theme_path)


@bot.event
async def on_command_error(_ctx, err):
    if isinstance(err, commands.CommandNotFound):
        return

    logging.warning(err)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot or after.afk:
        return

    if is_voice(after.channel) and after.channel != before.channel:
        theme_path = path.join(storage_dir, str(member.guild.id), str(member.id))
        if path.isfile(theme_path):
            voice = await join(after.channel)
            voice.play(FFmpegOpusAudio(theme_path), after=disconnect(voice))
        else:
            theme_path = path.join(storage_dir, str(member.guild.id), "global")
            if path.isfile(theme_path):
                voice = await join(after.channel)
                voice.play(FFmpegOpusAudio(theme_path), after=disconnect(voice))


async def join(channel):
    if (voice := discord.utils.get(bot.voice_clients, guild=channel.guild)) is not None:
        voice.pause()
        await voice.move_to(channel)
        return voice

    return await channel.connect(timeout=2.0)


def is_voice(channel):
    return channel is not None and not isinstance(channel, discord.StageChannel)


# https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function
def disconnect(voice):
    def voice_disconnect(play_err):
        if play_err is not None:
            logging.warning(play_err)

        asyncio.run_coroutine_threadsafe(voice.disconnect(), bot.loop)

    return voice_disconnect


bot.run(BOT_TOKEN)
