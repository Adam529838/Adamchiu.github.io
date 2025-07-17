import os
import discord
from discord.ext import commands
import json
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='!')

# 載入警告資料
try:
    with open('warnings.json', 'r') as f:
        warnings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    warnings = {}

def save_warnings():
    with open('warnings.json', 'w') as f:
        json.dump(warnings, f, indent=4)

@bot.event
async def on_ready():
    print(f'已登入為 {bot.user}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="未提供原因"):
    if str(member.id) not in warnings:
        warnings[str(member.id)] = []
    
    warnings[str(member.id)].append({
        "by": ctx.author.id,
        "reason": reason,
        "time": str(ctx.message.created_at)
    })
    
    save_warnings()
    await ctx.send(f"已警告 {member.mention}。原因: {reason}")

@bot.command()
async def warnings(ctx, member: discord.Member = None):
    member = member or ctx.author
    if str(member.id) not in warnings or not warnings[str(member.id)]:
        await ctx.send(f"{member.mention} 沒有任何警告記錄")
        return
    
    embed = discord.Embed(title=f"{member} 的警告記錄", color=0xff0000)
    for i, warning in enumerate(warnings[str(member.id)], 1):
        moderator = ctx.guild.get_member(warning['by'])
        moderator_name = moderator.name if moderator else "未知用戶"
        embed.add_field(
            name=f"警告 #{i}",
            value=f"由: {moderator_name}\n原因: {warning['reason']}\n時間: {warning['time']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def remove_warning(ctx, member: discord.Member, index: int):
    if str(member.id) not in warnings or index <= 0 or index > len(warnings[str(member.id)]):
        await ctx.send("無效的警告編號")
        return
    
    removed = warnings[str(member.id)].pop(index-1)
    save_warnings()
    
    await ctx.send(f"已移除 {member.mention} 的警告 #{index} (原因: {removed['reason']})")

bot.run(os.getenv('DISCORD_TOKEN'))
