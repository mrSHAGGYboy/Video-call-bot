"""
VideoPlayerBot, Telegram Video Chat Bot
Copyright (c) 2021  Asm Safone <https://github.com/AsmSafone>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import os
import time
import ffmpeg
import asyncio
from asyncio import sleep
from config import Config
from bot.video.nopm import User
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pytgcalls import GroupCallFactory
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ADMINS = Config.ADMINS
CHAT_ID = Config.CHAT_ID
USERNAME = Config.BOT_USERNAME

STREAM = {6}
VIDEO_CALL = {}

# PyTgCalls Client
group_call_factory = GroupCallFactory(User, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)

@Client.on_message(filters.command(["stream", f"stream@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def stream(client, m: Message):
    if 1 in STREAM:
        await m.reply_text("✅ **Please Stop The Existing Stream!**")
        return
    media = m.reply_to_message
    if not media:
        await m.reply_text("😕 **sorry it's not a video**\n\n» use the /stream command by replying to the video.")
        return
    elif media.video or media.document:
        msg = await m.reply_text("🔁 **Downloading video...**\n\n💭 __this process will take quite a while depending on the size of the video.__")
        if os.path.exists(f'stream-{CHAT_ID}.raw'):
            os.remove(f'stream-{CHAT_ID}.raw')
        try:
            video = await client.download_media(media)
            await msg.edit("⏳ **Converting video...**")
            os.system(f'ffmpeg -i "{video}" -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le -filter:a "atempo=0.81" stream-{CHAT_ID}.raw -y')
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n`{e}`")
            pass
        await sleep(5)
        group_call = group_call_factory.get_file_group_call(f'stream-{CHAT_ID}.raw')
        try:
            await group_call.start(CHAT_ID)
            await group_call.set_video_capture(video)
            VIDEO_CALL[CHAT_ID] = group_call
            await msg.edit("💡 **Video streaming started !**\n\n🟡 **join to video chat to watch the video.**")
            try:
                STREAM.remove(0)
            except:
                pass
            try:
                STREAM.add(1)
            except:
                pass
        except FloodWait as e:
            await sleep(e.x)
            if not group_call.is_connected:
                await group_call.start(CHAT_ID)
                await group_call.set_video_capture(video)
                VIDEO_CALL[CHAT_ID] = group_call
                await msg.edit("💡 **Video streaming started !**\n\n🟡 **join to video chat to watch the video.**")
                try:
                    STREAM.remove(0)
                except:
                    pass
                try:
                    STREAM.add(1)
                except:
                    pass
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n`{e}`")
            return
    else:
        await m.reply_text("😕 **sorry it's not a video**\n\n» use the /stream command by replying to the video.")
        return


@Client.on_message(filters.command(["mute", f"mute@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def mute(_, m: Message):
    if 0 in STREAM:
        await m.reply_text("✅ **Nothing to  Stream !**")
        return
    try:
        VIDEO_CALL[CHAT_ID].pause_playout()
        await m.reply_text("🔕 **Muted Streamer!**")
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n`{e}`")
        return

@Client.on_message(filters.command(["unmute", f"unmute@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def unmute(_, m: Message):
    if 0 in STREAM:
        await m.reply_text("✅ **Nothing to  Stream !**")
        return
    try:
        VIDEO_CALL[CHAT_ID].resume_playout()
        await m.reply_text("🔔 **Unmuted Streamer!**")
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n`{e}`")
        return

@Client.on_message(filters.command(["endstream", f"endstream@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def endstream(client, m: Message):
    if 0 in STREAM:
        await m.reply_text("✅ **Nothing to  Stream !**")
        return
    try:
        await VIDEO_CALL[CHAT_ID].stop()
        await m.reply_text("⏹️ **Streaming has ended !**\n\n✅ __userbot has been disconnected from the video chat__")
        try:
            STREAM.remove(1)
        except:
            pass
        try:
            STREAM.add(0)
        except:
            pass
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n`{e}`")
        return


admincmds=["stream", "pause", "resume", "endstream", f"stream@{USERNAME}", f"pause@{USERNAME}", f"resume@{USERNAME}", f"endstream@{USERNAME}"]

@Client.on_message(filters.command(admincmds) & ~filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def notforu(_, m: Message):
    k = await m.reply_sticker("CAACAgUAAx0CS6YhoQACog5hMX4Rpq7WaKlt4u3laQJ4apys8gACsAIAAj3CSFV4vqaasMUqMCAE")
    await sleep(5)
    await k.delete()
    try:
        await m.delete()
    except:
        pass

allcmd = ["start", "help", f"start@{USERNAME}", f"help@{USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~filters.chat(CHAT_ID))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/sl_bot_zone"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/slbotzone"),
            ],
            [
                InlineKeyboardButton("Source Code", url="https://github.com/youtubeslgeekshow/Video-call-bot"),
            ]
         ]
    await m.reply_text(text="**Sorry, You Can't Use This Bot In This Group! 🤷‍♂️ But You Can Make Your Own Bot Like This From The [Source Code](https://github.com/mrSHAGGYboy/Video-call-bot) 😉!**", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

