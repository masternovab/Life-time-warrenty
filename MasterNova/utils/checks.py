 sx4-discord-bot / Sx4
Code  Issues 0  Pull requests 0  Projects 0  Wiki  Pulse  Community
Sx4/utils/checks.py

from discord.ext import commands
import discord
import discord.utils
import json
import rethinkdb as r

def is_owner_check(ctx):
    if ctx.author.id in [477463812786618388]:
        return True
    else:
        return False

def is_main_owner():
    def predicate(ctx):
        if ctx.author.id in [477463812786618388]:
            return True
    return commands.check(predicate)

def is_owner():
    return commands.check(is_owner_check)

def is_owner_c(author):
    if author.id in [153286414212005888, 51766611097944064, 402557516728369153, 190551803669118976, 388424304678666240]:
        return True

def has_permissions(*perms):
    def predicate(ctx):
        serverdata = r.table("fakeperms").get(str(ctx.guild.id))
        role_perms = 0
        user_perms = 0
        if is_owner_check(ctx):
            return True
        elif ctx.author == ctx.guild.owner:
            return True
        elif serverdata.run():
            user = serverdata["users"].filter(lambda x: x["id"] == str(ctx.author.id))
            roles = serverdata["roles"]
            if user.run():
                user_perms = user[0]["perms"].run()
            for x in ctx.author.roles:
                if str(x.id) in roles.map(lambda x: x["id"]).run():
                    role_perms |= roles.filter(lambda y: y["id"] == str(x.id))[0]["perms"].run()
            perm_total = ctx.author.guild_permissions.value | user_perms | role_perms
            if discord.Permissions(perm_total).administrator:
                return True
            else:
                return all(getattr(discord.Permissions(perm_total), perm, None) for perm in perms)
        else:
            if ctx.author.guild_permissions.administrator:
                return True
            else:
                return all(getattr(ctx.author.guild_permissions, perm, None) for perm in perms)
    return commands.check(predicate)
 Desktop version Sign out
