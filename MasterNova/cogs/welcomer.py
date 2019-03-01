import discord
from discord.ext import commands
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
from utils import arghelp, dateify
from . import owner as dev
import math
from io import BytesIO
import logging
import rethinkdb as r
import requests
import cogs.image as img
from PIL import Image, ImageDraw, ImageFont, ImageOps
import asyncio
import random
import time

class welcomer:
    """Shows when a user joins and leaves a server"""

    def __init__(self, bot):
        self.bot = bot
        self.avatar = None

    @commands.group()
    @checks.has_permissions("manage_messages")
    async def imgwelcomer(self, ctx):
        """Make the bot welcome people for you with an image"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("welcomer").insert({"id": str(ctx.guild.id), "toggle": False, "channel": None,
            "message": "{user.mention}, Welcome to **{server}**. Enjoy your time here! The server now has {server.members} members.",
            "message-leave": "**{user.name}** has just left **{server}**. Bye **{user.name}**!", "dm": False, "imgwelcomertog": False, 
            "banner": None, "leavetoggle": True, "embed": False, "embedcolour": None}).run(durability="soft")

    @imgwelcomer.command(name="toggle")
    @checks.has_permissions("manage_messages")
    async def _toggle(self, ctx):
        "toggle image welcomer on or off"
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["imgwelcomertog"].run(durability="soft") == True:
            data.update({"imgwelcomertog": False}).run(durability="soft")
            await ctx.send("Image Welcomer has been **Disabled**")
            return
        if data["imgwelcomertog"].run(durability="soft") == False:
            data.update({"imgwelcomertog": True}).run(durability="soft")
            await ctx.send("Image Welcomer has been **Enabled**")
            return

    @imgwelcomer.command()
    @checks.has_permissions("manage_messages")
    async def banner(self, ctx, banner: str=None):
        """Adds a banner to the image welcomer, when added the image welcomer changes resolution to 2560 x 1440 so a banner that size would be ideal"""
        author = ctx.author
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not banner:
            if ctx.message.attachments:
                try: 
                    banner = ctx.message.attachments[0].url.replace(".gif", ".png").replace(".webp", ".png")
                    data.update({"banner": banner}).run(durability="soft")
                    return await ctx.send("Your banner for image welcomer has been set.")
                except:
                    pass
            data.update({"banner": None}).run(durability="soft")
            await ctx.send("Your banner for image welcomer has been reset.")
            return
        try:
            img.getImage(banner)
        except:
            await ctx.send("Invalid image url :no_entry:")
        data.update({"banner": banner}).run(durability="soft")
        await ctx.send("Your banner for image welcomer has been set.")

        
    @commands.group()
    async def welcomer(self, ctx):
        """Make the bot welcome people for you"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("welcomer").insert({"id": str(ctx.guild.id), "toggle": False, "channel": None,
            "message": "{user.mention}, Welcome to **{server}**. Enjoy your time here! The server now has {server.members} members.",
            "message-leave": "**{user.name}** has just left **{server}**. Bye **{user.name}**!", "dm": False, "imgwelcomertog": False, 
            "banner": None, "leavetoggle": True, "embed": False, "embedcolour": None}).run(durability="soft")
        
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def toggle(self, ctx): 
        """Toggle welcomer on or off"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["toggle"].run(durability="soft") == True:
            data.update({"toggle": False}).run(durability="soft")
            await ctx.send("Welcomer has been **Disabled**")
            return
        if data["toggle"].run(durability="soft") == False:
            data.update({"toggle": True}).run(durability="soft")
            await ctx.send("Welcomer has been **Enabled**")
            return

    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def embed(self, ctx):
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["embed"].run(durability="soft") == True:
            data.update({"embed": False}).run(durability="soft")
            await ctx.send("Welcome messages will no longer be embedded.")
            return
        if data["embed"].run(durability="soft") == False:
            data.update({"embed": True}).run(durability="soft")
            await ctx.send("Welcome messages will now be embedded.")
            return

    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def embedcolour(self, ctx, colour: str):
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if colour.lower() in ["none", "off"]:
            await ctx.send("Your embed colour has been reset.")
            return data.update({"embedcolour": None}).run(durability="soft")
        if colour.startswith("#"):
            colour = colour[1:]
        try:
            discord.Colour(int(colour, 16))
        except:
            return await ctx.send("Invalid hex :no_entry:")
        await ctx.send("Updated your embed colour to **{}**".format(str(colour)))
        data.update({"embedcolour": int(colour, 16)}).run(durability="soft")

    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def dmtoggle(self, ctx): 
        """Toggle whether you want the bot to dm the user or not"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["dm"].run(durability="soft") == True:
            data.update({"dm": False}).run(durability="soft")
            await ctx.send("Welcome messages will now be sent in the welcomer channel.")
            return
        if data["dm"].run(durability="soft") == False:
            data.update({"dm": True}).run(durability="soft")
            await ctx.send("Welcome messages will now be sent in dms.")
            return

    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def leavetoggle(self, ctx):
        """Toggle if you want the leave message or not"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["leavetoggle"].run(durability="soft") == True:
            data.update({"leavetoggle": False}).run(durability="soft")
            await ctx.send("Leave messages are now disabled.")
            return
        if data["leavetoggle"].run(durability="soft") == False:
            data.update({"leavetoggle": True}).run(durability="soft")
            await ctx.send("Leave messages are now enabled.")
            return
    
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def joinmessage(self, ctx, *, message: str=None):
        """Set the joining message"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
{server.members.prefix} = The amount of members plus a prefix ex 232nd
{user.created.length} = How long the users account has been created for ex 1 year 2 months 3 days
**Make sure you keep the {} brackets in the message**
Example: `s?welcomer joinmessage {user.mention}, Welcome to **{server}**. We now have **{server.members}** members :tada:`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
            return
        data.update({"message": message}).run(durability="soft")
        await ctx.send("Your message has been set <:done:403285928233402378>")
        
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def leavemessage(self, ctx, *, message: str=None):
        """Set the leaving message"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
{server.members.prefix} = The amount of members plus a prefix ex 232nd
{user.created.length} = How long the users account has been created for ex 1 year 2 months 3 days
**Make sure you keep the {} brackets in the message**
Example: `s?welcomer leavemessage {user.mention}, Goodbye!`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
            return
        data.update({"message-leave": message}).run(durability="soft")
        await ctx.send("Your message has been set <:done:403285928233402378>")
        
    @welcomer.command()
    async def preview(self, ctx):
        """Look at the preview of your welcomer"""
        server = ctx.guild
        author = ctx.author
        data = r.table("welcomer").get(str(server.id)).run(durability="soft")
        message = data["message"]
        message = message.replace("{server}", server.name)
        message = message.replace("{user.mention}", author.mention)
        message = message.replace("{user.name}", author.name)
        message = message.replace("{user}", str(author))
        message = message.replace("{server.members}", "{:,}".format(len(server.members))) 
        message = message.replace("{server.members.prefix}", self.prefixfy(server)) 
        message = message.replace("{user.created.length}", dateify.get((datetime.utcnow() - author.created_at).total_seconds()))
        message2 = data["message-leave"]
        message2 = message2.replace("{server}", server.name)
        message2 = message2.replace("{user.mention}", author.mention)
        message2 = message2.replace("{user.name}", author.name)
        message2 = message2.replace("{user}", str(author))
        message2 = message2.replace("{server.members}", "{:,}".format(len(server.members)))
        message2 = message2.replace("{server.members.prefix}", self.prefixfy(server)) 
        message2 = message2.replace("{user.created.length}", dateify.get((datetime.utcnow() - author.created_at).total_seconds()))
        s=discord.Embed(description=message, timestamp=datetime.utcnow(), colour=discord.Colour(data["embedcolour"]) if data["embedcolour"] else discord.Embed.Empty)
        s.set_author(name=str(author), icon_url=author.avatar_url)
        if data["imgwelcomertog"] and data["toggle"]:
            if data["embed"]:
                await ctx.send(embed=s, file=self.image_welcomer(author, server))
            else:
                await ctx.send(content=message, file=self.image_welcomer(author, server))
        elif data["imgwelcomertog"] and not data["toggle"]:
            await ctx.send(file=self.image_welcomer(author, server))
        elif not data["imgwelcomertog"] and data["toggle"]:
            if data["embed"]:
                await ctx.send(embed=s)
            else:
                await ctx.send(message)
        else:
            return await ctx.send("You have neither image welcomer or welcomer enabled :no_entry:")
        if data["leavetoggle"]:
            if data["embed"]:
                await ctx.send(embed=s)
            else:
                await ctx.send(message2)
            
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel of where you want the bot to welcome people"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        data.update({"channel": str(channel.id)}).run(durability="soft")       
        await ctx.send("<#{}> has been set as the join-leave channel".format(channel.id))
        
    @welcomer.command()
    async def stats(self, ctx): 
        """Look at the settings of your welcomer"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id)).run(durability="soft")
        message = "`" + data["message"] + "`"
        message2 = "`" + data["message-leave"] + "`"  
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Welcomer Settings", icon_url=self.bot.user.avatar_url)
        if data["toggle"] == True:
            msg = "Enabled"
        if data["toggle"] == False:
            msg = "Disabled"
        if data["dm"] == True:
            msg2 = "Enabled"
        if data["dm"] == False:
            msg2 = "Disabled"
        if data["imgwelcomertog"] == True:
            img = "Enabled"
        else:
            img = "Disabled"
        if data["leavetoggle"] == False:
            message2 = "Disabled"
        s.add_field(name="Welcomer status", value=msg)
        if not data["channel"]:
            channel = "Not set"
        else:
            channel = "<#{}>".format(data["channel"])
        s.add_field(name="Welcomer channel", value=channel)
        s.add_field(name="DM Welcomer", value=msg2)
        s.add_field(name="Image Welcomer", value=img)
        s.add_field(name="Embed", value="Message: {}\nColour: {}".format("Yes" if data["embed"] else "No", discord.Colour(data["embedcolour"]) if data["embedcolour"] else "Default"))
        s.add_field(name="Join message", value=message, inline=False)
        s.add_field(name="Leave message", value=message2, inline=False)
        await ctx.send(embed=s)
        
    def prefixfy(self, server):
        number = str(len(server.members))
        num = len(number) - 2
        num2 = len(number) - 1
        if int(number[num:]) < 11 or int(number[num:]) > 13:
            if int(number[num2:]) == 1:
                prefix = "st"
            elif int(number[num2:]) == 2:
                prefix = "nd"
            elif int(number[num2:]) == 3:
                prefix = "rd"
            else:
                prefix = "th"
        else:
            prefix = "th"
        return "{:,}".format(int(number)) + prefix
        
        
    async def on_member_join(self, member): 
        server = member.guild
        data = r.table("welcomer").get(str(server.id)).run(durability="soft")
        message = data["message"]
        channel = data["channel"]
        channel = server.get_channel(int(channel))
        if not channel:
            if server.system_channel:
                channel = server.system_channel
        message = message.replace("{server}", server.name)
        message = message.replace("{user.mention}", member.mention)
        message = message.replace("{user.name}", member.name)
        message = message.replace("{user}", str(member))
        message = message.replace("{server.members}", "{:,}".format(len(server.members)))
        message = message.replace("{server.members.prefix}", self.prefixfy(server)) 
        message = message.replace("{user.created.length}", dateify.get((datetime.utcnow() - member.created_at).total_seconds()))
        s=discord.Embed(description=message, timestamp=datetime.utcnow(), colour=discord.Colour(data["embedcolour"]) if data["embedcolour"] else discord.Embed.Empty)
        s.set_author(name=str(member), icon_url=member.avatar_url)
        if data["toggle"] == True and data["imgwelcomertog"] == True:
            if data["dm"] == True:
                if data["embed"]:
                    await member.send(embed=s, file=self.image_welcomer(member, server))
                else:
                    await member.send(content=message, file=self.image_welcomer(member, server))
            elif data["dm"] == False:
                if data["embed"]:
                    await self.webhook_send(channel=channel, embed=s, file=self.image_welcomer(member, server))
                else:
                    await self.webhook_send(channel=channel, content=message, file=self.image_welcomer(member, server))
        elif data["toggle"] == True and data["imgwelcomertog"] == False:
            if data["dm"] == True:
                if data["embed"]:
                    await member.send(embed=s)
                else:
                    await member.send(content=message)
            elif data["dm"] == False:
                if data["embed"]:
                    await self.webhook_send(channel=channel, embed=s)
                else:
                    await self.webhook_send(channel=channel, content=message)
        elif data["toggle"] == False and data["imgwelcomertog"] == True:
            if data["dm"] == True:
                await member.send(file=self.image_welcomer(member, server))
            elif data["dm"] == False:
                await self.webhook_send(channel=channel, file=self.image_welcomer(member, server))    
            
    async def on_member_remove(self, member):
        server = member.guild
        data = r.table("welcomer").get(str(server.id)).run(durability="soft")
        if data["dm"] == True:
            return
        if data["leavetoggle"] == False:
            return
        channel = data["channel"]
        channel = server.get_channel(int(channel))
        if not channel:
            if server.system_channel:
                channel = server.system_channel
        message = data["message-leave"]
        if data["toggle"] == True:
            message = message.replace("{server}", server.name)
            message = message.replace("{user.mention}", member.mention)
            message = message.replace("{user.name}", member.name)
            message = message.replace("{user}", str(member))
            message = message.replace("{server.members}", "{:,}".format(len(server.members)))
            message = message.replace("{server.members.prefix}", self.prefixfy(server)) 
            message = message.replace("{user.created.length}", dateify.get((datetime.utcnow() - member.created_at).total_seconds()))
            if data["embed"]:
                s=discord.Embed(description=message, timestamp=datetime.utcnow(), colour=discord.Colour(data["embedcolour"]) if data["embedcolour"] else discord.Embed.Empty)
                s.set_author(name=str(member), icon_url=member.avatar_url)
                await self.webhook_send(channel=channel, embed=s)
            else:
                await self.webhook_send(channel=channel, content=message)

    def image_welcomer(self, author, server):
        data = r.table("welcomer").get(str(server.id)).run(durability="soft")
        name = author.name
        def circlefy(image):
            size = (image.size[0] * 6, image.size[1] * 6)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + size, fill=255)
            mask = mask.resize(image.size)
            image.putalpha(mask)
            return image
        x = 440
        y = 410
        wel = 475
        z = 0
        if data["banner"]:
            try:
                background = img.getImage(data["banner"])
                background = background.resize((2560, 1440))
                trans = 200
            except:
                background = Image.new('RGBA', (2560, 630), (0, 0, 0, 0))
                trans = 200
                z += 5
                y -= 405
                x -= 405
                wel -= 405
        else:
            background = Image.new('RGBA', (2560, 630), (0, 0, 0, 0))
            trans = 200
            z += 5
            y -= 405
            x -= 405
            wel -= 405
        outline = Image.new("RGBA", (620, 620), (255, 255, 255))
        rectangle = Image.new("RGBA", (2560, 560), (0, 0, 0, trans))
        W, H = (2840, 560)
        outline = circlefy(outline)
        avatar = img.getImage(author.avatar_url)
        avatar = avatar.resize((600, 600))
        avatar = circlefy(avatar)
        background.paste(rectangle, (350 + z, x), rectangle)
        outline.paste(avatar, (10, 10), avatar)
        background.paste(outline, (z, y), outline)
        draw = ImageDraw.Draw(background)
        size = 200
        for i, somethingrandom in enumerate(name):
            if i >= 12 and i < 16:
                size -= 12
            elif i >= 16 and i < 23:
                size -= 7
            elif i >= 23 and i < 28:
                size -= 6
        if size < 0:
            return
        font = ImageFont.truetype("uni-sans.otf", 100)
        font2 = ImageFont.truetype("uni-sans.otf", size)
        w, h = font2.getsize(name)
        w2, h2 = font.getsize("Welcome")
        w3, h3 = font.getsize("#" + author.discriminator)
        draw.text(((W-w2)/2, wel), "Welcome", (255, 255, 255), font=font)
        draw.text(((W-w)/2, x + (H-h)/2), name, (255, 255, 255), font=font2)
        draw.text(((W-w)/2 + w, x + (H-h)/2 + (154 if size == 200 else h)-h3), "#" + author.discriminator, (153, 170, 181), font=font)
        temp = BytesIO()
        background.save(temp, "png")
        temp.seek(0)
        return discord.File(temp, "result.png")

    async def webhook_send(self, channel, content=None, file=None, embed=None):
        if self.avatar is None:
            try:
                with open("sx4-byellow.png", "rb") as f:
                    self.avatar = f.read()
            except:
                pass
        webhook = discord.utils.get(await channel.guild.webhooks(), name="Sx4 - Welcomer")
        if not webhook:
            webhook = await channel.create_webhook(name="Sx4 - Welcomer", avatar=self.avatar)
        elif webhook and channel != webhook.channel:
            await webhook.delete()
            webhook = await channel.create_webhook(name="Sx4 - Welcomer", avatar=self.avatar)
        await webhook.send(content=content, file=file, embed=embed)

def setup(bot): 
    bot.add_cog(welcomer(bot))
