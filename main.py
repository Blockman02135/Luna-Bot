import discord, asyncio, os, json, math, sqlite3, random as r
from discord.ext import commands
from discord import utils

mconn = sqlite3.connect("members.db")
mcursor = mconn.cursor()

mcursor.execute("""CREATE TABLE IF NOT EXISTS member (
                id text,
                guild text,
                money int,
                bonus int,
                level int,
                exp int,
                cjob text)""")
mconn.commit()

gconn = sqlite3.connect("guilds.db")
gcursor = gconn.cursor()

gcursor.execute("""CREATE TABLE IF NOT EXISTS guild (
                id text,
                work_c int,
                log_c int,
                suggest_c int,
                mute_role int,
                shop text
                )""")
gconn.commit()

luna_m = "Luna Moderator"

def gi(path,oname):
  with open(path,"r") as f:
    data = json.load(f)
    decode = str(data).replace("'",'"')
    if (decode.find(f'"{oname.lower()}": '+'{') != -1):
      return data[oname]
    else:
      return False

def new_i(path,id,name,count):
  with open(path, 'r') as f:
    data = json.load(f)
    decode = str(data).replace("'",'"')
    if (decode.find(f'"{id.lower()}": '+'{') != -1):
      common = {
        "name":name,
        "count":gi(path,id)["count"]+int(count)
      }
    else:
      common = {
        "name":name,
        "count":int(count)
      }
    data[id] = common
    data = str(data).replace("'", '"')
    return data

def rem_i(path,id,count):
  with open(path, 'r') as f:
    data = json.load(f)
    decode = str(data).replace("'",'"')
    if (decode.find(f'"{id.lower()}": '+'{') != -1):
      if (count<0):
        del data[id]
      else:
        data[id]["count"]-=count
    else:
      return False
    data = str(data).replace("'", '"')
    return data

def new_t(path,oname,name,price):
  with open(path, 'r') as f:
    data = json.load(f)
    common = {
      "name":name,
      "price":int(price)
    }
    data[oname] = common
    data = str(data).replace("'", '"')
    return data

def rem_t(path,oname):
  with open(path, 'r') as f:
    data = json.load(f)
    decode = str(data).replace("'",'"')
    if (decode.find(f'"{oname.lower()}": '+'{') != -1):
      del data[oname]
    else:
      return False
    data = str(data).replace("'", '"')
    return data

def glist(path,size):
  with open(path,"r") as f:
    code = f.read()
    if (code=="{}"):
      return -1
    data = json.loads(code)
    size = math.inf if size < 0 else size
    loop=0
    result = [];
    for item in data:
      if (loop<size):
        result.append([item,gi(path,str(item))])
        loop+=1
    if (len(result)>0):
      return result
    else:
      return False

def check():
  for guild in Bot.guilds:
    if (not os.path.isfile(f'./shops/{guild.id}.json')):
      file = open(f"shops//{guild.id}.json","w")
      file.write("{}")
      file.close()
    insert = [(guild.id, None, None, None, None, None)]
    gcursor.execute(f"SELECT id FROM guild WHERE id={guild.id}")
    if gcursor.fetchone() == None:
      gcursor.executemany("INSERT INTO guild VALUES (?,?,?,?,?,?)", insert)
      gconn.commit()
    for member in guild.members:
      if (not os.path.isfile(f'./invs/{member.id}.json')):
        file = open(f"invs//{member.id}.json","w")
        file.write("{}")
        file.close()
      insert = [(member.id, guild.id, 5, 0, 1, 0, None)]
      mcursor.execute(f"SELECT id FROM member WHERE id={member.id} AND guild={guild.id}")
      if mcursor.fetchone() == None:
        mcursor.executemany("INSERT INTO member VALUES (?,?,?,?,?,?,?)", insert)
        mconn.commit()

common_prefix = '&'
Bot = commands.Bot(command_prefix=common_prefix)
Bot.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        Bot.load_extension(f'cogs.{filename[:-3]}')

@Bot.event
async def on_ready():
    print(f"[SYSTEM] Bot online!\n[SYSTEM] Name - {Bot.user}\n[SYSTEM] ID - {Bot.user.id}")
    while True:
      await asyncio.sleep(1)
      await Bot.change_presence(activity= discord.Activity(name= f'{len(Bot.guilds)} servers | {common_prefix}help', type= discord.ActivityType.watching),status= discord.Status.idle)
      check()

@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send(embed=discord.Embed(description=f'{ctx.message.author.mention}, command not found!'))
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(description=f'{ctx.message.author.mention}, command syntax error! `{common_prefix}help` to open help menu!'))

@Bot.event
async def on_guild_join(guild):
  print(f"[AUTHORISATION] {Bot.user} joined the server: {guild.name}!")

jobs = [['miner','mine',0.01,1,None],['hunter','hunt',0.5,1.9,50],['builder','build',1,1.6,150],['destroyer','destroy',2,3.3,300]]

@Bot.event
async def on_message(message):
  check()
  for c in gcursor.execute(f"SELECT work_c FROM guild WHERE id={message.guild.id}"):
    ch=c
  a = []
  for i in message.content:
    a.append(i)
  mprefix=''.join(a[slice(0,len(common_prefix))])
  if (len(message.content) > 5 and not mprefix==common_prefix and message.channel.id !=ch[0]):
    for row in mcursor.execute(f"""SELECT id,guild,money,bonus,level,exp FROM member WHERE id={message.author.id} AND guild={message.guild.id}"""):
      exp = row[5]+r.randint(1, 6)
      mcursor.execute(f"""UPDATE member SET exp={exp} WHERE id={message.author.id} AND guild={message.guild.id}""")
      mconn.commit()
      needexp = row[4]*50
      if (exp >= needexp):
        mcursor.execute(f"""UPDATE member SET level={row[4]+1} WHERE id={message.author.id} AND guild={message.guild.id}""")
        mcursor.execute(f"""UPDATE member SET exp={exp-needexp} WHERE id={message.author.id} AND guild={message.guild.id}""")
        money = row[2]+round(r.uniform(0, 2),3)*(row[3]+1)
        mcursor.execute(f"""UPDATE member SET money={money} WHERE id={message.author.id} AND guild={message.guild.id}""")
        mconn.commit()
        await message.author.send(f"Congratulations! You got a level **{row[4]+1}** on the server: **{message.guild}**!")
  if message.channel.id ==ch[0] and not message.author==Bot.user:
    for j in mcursor.execute(f"SELECT cjob FROM member WHERE id={message.author.id} AND guild={message.guild.id}"):
      job = str(j[0])
      for jj in jobs:
        if (jj[0]==job):
          word = jj[1]
          if (message.content==word):
            for cash in mcursor.execute(f"""SELECT money, bonus FROM member WHERE id={message.author.id} AND guild={message.guild.id}"""):
              salary = round(r.uniform(jj[2], jj[3]),3)*(cash[1]+1)
              mcursor.execute(f"""UPDATE member SET money={cash[0]+salary} WHERE id={message.author.id} AND guild={message.guild.id}""")
              mconn.commit()
              await message.channel.send(f"**{message.author.name}**, you earned **{salary}**:small_orange_diamond:! Now you have **{cash[0]+salary}**:small_orange_diamond:")
  await Bot.process_commands(message)

from Cybernator import Paginator

@Bot.command()
async def help(ctx):
    page_1 = discord.Embed(
        title= 'Economy',
        description= f'```prefix - {common_prefix}```'
    )
    page_1.add_field(
        name= '&help',
        value= 'Open this menu.'
    )
    page_1.add_field(
        name= '&setshop [add/rem/list] [arguments]',
        value= 'Configurate the shop.'
    )
    page_1.add_field(
        name= '&config [property] [value]',
        value= 'Server configuration.'
    )
    page_1.add_field(
        name= '&setStats [member] [property] [value]',
        value= "Configurate member's values."
    )
    page_1.add_field(
        name= '&inv',
        value= 'Shows your inventory.'
    )
    page_1.add_field(
        name= '&job [join/list] (job)',
        value= 'Join or see all jobs.'
    )
    page_1.add_field(
        name= '&shop [buy/list] (item)',
        value= 'Buy item.'
    )
    page_2 = discord.Embed(
        title= 'Moderation',
        description= f'```prefix - {common_prefix}```'
    )
    page_2.add_field(
        name= '&say [message]',
        value= 'Send the message by bot.'
    )
    page_2.add_field(
        name= '&muterole [add/set] [name/id]',
        value= 'Creates or sets mute role.'
    )
    page_2.add_field(
        name= '&mute [member] (reason)',
        value= 'Mutes member.'
    )
    page_2.add_field(
        name= '&unmute [member]',
        value= 'Unmutes member.'
    )
    page_2.add_field(
        name= '&kick [member] (reason)',
        value= 'Kicks member.'
    )
    page_2.add_field(
        name= '&ban [member] (reason)',
        value= 'Bans member.'
    )
    page_2.add_field(
        name= '&unban [member/id]',
        value= 'Unbans member.'
    )
    page_2.add_field(
        name= '&tempban [member] [time] [s/m/h/d] (reason)',
        value= 'Tempbans member.'
    )

    msg = await ctx.send(embed= page_1)

    comp_help = Paginator(Bot, msg, only= ctx.author, embeds= [page_1, page_2],language= "en")

    await comp_help.start()

@Bot.command()
async def job(ctx,what,value=None):
  what=what.lower()
  if (what=="join"):
    if (value==None):
      msg =discord.Embed(title="Jobs",color=0xfff000)
      for job in jobs:
        msg.add_field(
          name=job[0],
          value=f':small_orange_diamond:**[{job[2]}-{job[3]}]**   :small_orange_diamond:**{"FREE" if(job[4]==None) else job[4]}**\n',
          inline= False
          )
      return await ctx.send(embed=msg)
    value=value.lower()
    f=False
    for job in jobs:
      if (value==job[0]):
        f=True
        curjob=None
        for j in mcursor.execute(f"SELECT cjob FROM member WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}"):
          curjob = str(j[0])
        if (curjob==value):
          return await ctx.send(":no_entry_sign:You are already joined to this job!")
        for money in mcursor.execute(f"SELECT money FROM member WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}"):
          if (not job[4]==None and money[0] < job[4]):
            return await ctx.send(f"To join this job you must have **{job[4]}**:small_orange_diamond: but now you have **{money[0]}**:small_orange_diamond:")
        for money in mcursor.execute(f"SELECT money FROM member WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}"):
          if (not job[4]==None):
            mcursor.execute(f"""UPDATE member SET money={money[0]-job[4]} WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}""")
        mcursor.execute(f"""UPDATE member SET cjob="{value}" WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}""")
        mconn.commit()
        await ctx.send(f"You joined to new job!\nJob: **{job[0]}**\nMin salary: :small_orange_diamond:**{job[2]}**\nMax salary: :small_orange_diamond:**{job[3]}**\nSend `{job[1]}` to the work channel to work!")
    if (not f):
      await ctx.send("I can't find this job:face_with_monocle:")
      msg =discord.Embed(title="Jobs",color=0xfff000)
      for job in jobs:
        msg.add_field(
          name=job[0],
          value=f':small_orange_diamond:**[{job[2]}-{job[3]}]**   :small_orange_diamond:**{"FREE" if(job[4]==None) else job[4]}**\n',
          inline= False
          )
      return await ctx.send(embed=msg)
  if (what=="currnet"):
    for j in mcursor.execute(f"SELECT cjob FROM member WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}"):
      if (j[0]==None):
        return await ctx.send("You are not joined to job!\n`&job join [job]` to join.")
      for job in jobs:
        if (job[0]==j[0]):
          await ctx.send(f"Your current job is **{job[0]}**\nJob: **{job[0]}**\nMin salary: **{job[2]}**\nMax salary: **{job[3]}**\nSend `{job[1]}` to the work channel to work!")

@Bot.command()
async def inv(ctx):
  path = f"invs//{ctx.message.author.id}.json"
  data = glist(path,-1)
  if (data==-1):
    return await ctx.send("Your inventory is empty.")
  emb = discord.Embed(
    title= f"{ctx.message.author.name}'s Inventory",
    colour= (r.randint(0,16777215)),
    description= f"{len(glist(path,-1))} Items"
  )
  for line in data:
    name = line[1]["name"]
    count = line[1]["count"]
    emb.add_field(
      name=line[0].upper(),
      value=f"Name: **{name}**\nCount: **{count}**",
      inline= False
    )
    emb.set_thumbnail(url=ctx.message.author.avatar_url)
  return await ctx.send(embed=emb)

@Bot.command()
async def shop(ctx,*,args):
  path = f"shops//{ctx.guild.id}.json"
  args=args.split(' ')
  if (args[0]=="list"):
    data = glist(f"shops//{ctx.guild.id}.json",-1)
    if (data==-1):
      return await ctx.send("0 Items!\n`&setshop add [table-name] [name] [price]` to create one!")
    emb = discord.Embed(
      title= f"{ctx.guild.name}'s SHOP",
      colour= (r.randint(0,16777215)),
      description= f"{len(glist(path,-1))} Items"
    )
    for line in data:
      name = line[1]["name"]
      price = line[1]["price"]
      emb.add_field(
        name=line[0].upper(),
        value=f"Name: **{name}**\nPrice: **{price}:small_orange_diamond:**\n`&shop buy {line[0].lower()}` - To buy item!",
        inline= False
      )
    emb.set_thumbnail(url=ctx.guild.icon_url)
    return await ctx.send(embed=emb)
  elif (args[0]=="buy"):
    if (args[1]==None):
      return await ctx.send("Please enter a item name!")
      args[1]=args[1].lower()
    item = gi(path,args[1].lower())
    if (item):
      name = item["name"]
      price = item["price"]
      for money in mcursor.execute(f"SELECT money FROM member WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}"):
        if (int(money[0])>=price):
          mcursor.execute(f"""UPDATE member SET money={int(money[0]-price)} WHERE id={ctx.message.author.id} AND guild={ctx.guild.id}""")
          mconn.commit()
          data = new_i(f"invs//{ctx.message.author.id}.json",name.lower(),name,1)
          file = open(f"invs//{ctx.message.author.id}.json","w")
          file.write(data)
          file.close()
          await ctx.send(f"You bought a **{name}**! Your money is removed **{price}**:small_orange_diamond:")
        else:
          return await ctx.send(f"You need :small_orange_diamond:**{price}** to buy **{name}** but now you have :small_orange_diamond:**{money[0]}**")
    else:
      return await ctx.send("I can't find this item:face_with_monocle:")

@Bot.command()
async def setshop(ctx,*,args):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  path = f"shops//{ctx.guild.id}.json"
  args=args.split(' ')
  if (args[0]=="clear"):
    file = open(f"shops//{ctx.guild.id}.json","w")
    file.write("{}")
    file.close()
    return await ctx.send("Shop cleared!")
  elif (args[0]=="add" and args[1] and args[2] and args[3]):
    data = new_t(path,args[1].lower(),args[2],int(args[3]))
    file = open(f"shops//{ctx.guild.id}.json","w")
    file.write(data)
    file.close()
    return await ctx.send(f"Added new item!\nName: **{args[2]}**\nPrice: **{args[3]}**:small_orange_diamond:\nTable name: `{args[1].lower()}`")
  elif (args[0]=="getItem" and args[1]):
    if (args[1]==None):
      return await ctx.send("Please enter a item name!")
    item = gi(path,args[1].lower())
    if (item):
      name = item["name"]
      price = item["price"]
      return await ctx.send(f"==={args[1].upper()}===\nName: **{name}**\nPrice: **{price}:small_orange_diamond:**\nTable name: `{args[1].lower()}`")
    else:
      return await ctx.send("I can't find this item:face_with_monocle:")
  elif (args[0]=="del" and args[1]):
    item = rem_t(path,args[1].lower())
    if (item):
      file = open(f"shops//{ctx.guild.id}.json","w")
      file.write(item)
      file.close()
      return await ctx.send(f"Removed item: **{args[1].lower()}**")
    else:
      return await ctx.send("I can't find this item:face_with_monocle:")
  elif (args[0]=="list"):
    data = glist(f"shops//{ctx.guild.id}.json",-1)
    if (data==-1):
      return await ctx.send("0 Items!\n`&setshop add [table-name] [name] [price]` to create one!")
    emb = discord.Embed(
      title= f"{ctx.guild.name}'s SHOP",
      colour= (r.randint(0,16777215)),
      description= f"{len(glist(path,-1))} Items"
    )
    for line in data:
      name = line[1]["name"]
      price = line[1]["price"]
      emb.add_field(
        name=line[0].upper(),
        value=f"Name: **{name}**\nPrice: **{price}:small_orange_diamond:**\n`&shop buy {line[0].lower()}` - To buy item!",
        inline= False
      )
    emb.set_thumbnail(url=ctx.guild.icon_url)
    return await ctx.send(embed=emb)

@Bot.command()
async def config(ctx, config, *, value):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  if config=="setSuggestID":
    value = int(value)
    gcursor.execute(f"""UPDATE guild SET suggest_c={value} WHERE id={ctx.guild.id}""")
    for row in gcursor.execute(f"""SELECT suggest_c FROM guild WHERE id={ctx.guild.id}"""):
      await ctx.send("ID **Suggest** channel: **"+str(row[0])+"**")
  elif config=="setLogID":
    value = int(value)
    gcursor.execute(f"""UPDATE guild SET log_c={value} WHERE id={ctx.guild.id}""")
    for row in gcursor.execute(f"""SELECT log_c FROM guild WHERE id={ctx.guild.id}"""):
      await ctx.send("ID **Logs** channel: **"+str(row[0])+"**")
    gconn.commit()
  elif config=="setWorkID":
    value=int(value)
    gcursor.execute(f"""UPDATE guild SET work_c={value} WHERE id={ctx.guild.id}""")
    for row in gcursor.execute(f"""SELECT work_c FROM guild WHERE id={ctx.guild.id}"""):
      await ctx.send("ID **Work** channel: **"+str(row[0])+"**")
    gconn.commit()

@Bot.command()
async def bal(ctx,member: discord.Member):
  member = ctx.message.author if member == None else member
  for cash in mcursor.execute(f"""SELECT money, bonus FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
    emb = discord.Embed(
      title= f"{member}'s balance",
      color= member.color
    )
    emb.add_field(
      name= "Money",
      value= f"{cash[0]}:small_orange_diamond:",
      inline= False
    )
    emb.add_field(
      name= "Bonus",
      value= f"x{cash[1]}:arrow_double_up:",
      inline= False
    )
    await ctx.send(embed=emb)
  
@Bot.command()
async def balance(ctx,member: discord.Member):
  member = ctx.message.author if member == None else member
  for cash in mcursor.execute(f"""SELECT money, bonus FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
    emb = discord.Embed(
      title= f"{member}'s balance",
      color= member.color
    )
    emb.add_field(
      name= "Money",
      value= f"{cash[0]}:small_orange_diamond:",
      inline= False
    )
    emb.add_field(
      name= "Bonus",
      value= f"x{cash[1]}:arrow_double_up:",
      inline= False
    )
    await ctx.send(embed=emb)

@Bot.command()
async def getMember(ctx, member: discord.Member):
  check()
  for row in mcursor.execute(f"SELECT id,guild,money,bonus,level,exp,cjob FROM member WHERE id={member.id} AND guild={ctx.guild.id}"):
    emb = discord.Embed(
      title= f"===**{member}**===",
      color= member.color
    )
    emb.add_field(
      name= 'Name',
      value= member.name,
      inline= False
    )
    emb.add_field(
      name= 'Discriminator',
      value= member.discriminator,
      inline= False
    )
    emb.add_field(
      name= 'ID',
      value= member.id,
      inline= False
    )
    emb.add_field(
      name= 'Job',
      value= row[6],
      inline= False
    )
    emb.add_field(
      name= 'Money',
      value= str(row[2]),
      inline= False
    )
    emb.add_field(
      name= 'Bonus',
      value= str(row[3]),
      inline= False
    )
    emb.add_field(
      name= 'Level',
      value= row[4],
      inline= False
    )
    emb.add_field(
      name= 'EXP',
      value= f"{row[5]}/{row[4]*50}",
      inline= False
    )
    emb.set_thumbnail(url= member.avatar_url)
    await ctx.send(embed=emb)

@Bot.command()
async def setStats(ctx, member : discord.Member, what,*, value=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  if (value==None):
    await ctx.send(f'{ctx.message.author.mention}, please enter a value!')
  else:
    if (what.lower()=="money"):
      mcursor.execute(f"""UPDATE member SET money={int(value)} WHERE id={member.id} AND guild={ctx.guild.id}""")
      mconn.commit()
      for row in mcursor.execute(f"""SELECT money FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
        await ctx.send(f"Now {member.mention} has **{str(row[0])}** Money")
    elif (what.lower()=="bonus"):
      mcursor.execute(f"""UPDATE member SET bonus={int(value)} WHERE id={member.id} AND guild={ctx.guild.id}""")
      mconn.commit()
      for row in mcursor.execute(f"""SELECT bonus FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
        await ctx.send(f"Now {member.mention} has **x{str(row[0])}** Bonus")
    elif (what.lower()=="level" or what.lower()=="lvl"):
      mcursor.execute(f"""UPDATE member SET level={int(value)} WHERE id={member.id} AND guild={ctx.guild.id}""")
      mconn.commit()
      for row in mcursor.execute(f"""SELECT level FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
        await ctx.send(f"Now {member.mention} has **{str(row[0])}** Level")
    elif (what.lower()=="exp"):
      mcursor.execute(f"""UPDATE member SET exp={int(value)} WHERE id={member.id} AND guild={ctx.guild.id}""")
      mconn.commit()
      for row in mcursor.execute(f"""SELECT exp FROM member WHERE id={member.id} AND guild={ctx.guild.id}"""):
        await ctx.send(f"Now {member.mention} has **{str(row[0])}** EXP")

@Bot.command()
async def suggest( ctx , * , agr ):
  for row in gcursor.execute(f"""SELECT suggest_c FROM guild WHERE id={ctx.guild.id}"""):
    if (row[0]==None):
      return await ctx.send("Set suggest channel!\n`&config setSuggestID [id]`")
    suggest_chanell = Bot.get_channel(row[0]) #Айди канала предложки
    embed = discord.Embed(title=f"{ctx.author.name} Предложил :", description= f" {agr} \n\n")

    embed.set_thumbnail(url=ctx.guild.icon_url)

    message = await suggest_chanell.send(embed=embed)
    await message.add_reaction('☑️')
    await message.add_reaction('❎')

@Bot.command()
@commands.has_guild_permissions(administrator= True)
async def muterole(ctx, what, *, args):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  args = args.split(' ')
  if (what.lower()=="add"):
    mute_role = await ctx.guild.create_role(name=' '.join(args), permissions=discord.Permissions(permissions=0))
    gcursor.execute(f"""UPDATE guild SET mute_role={mute_role.id} WHERE id={ctx.guild.id}""")
    gconn.commit()
    await ctx.send(f"The mute role has been successfully created.\nName: **{mute_role.name}**\nID: **{mute_role.id}**\n<@&{mute_role.id}>")
  elif (what.lower()=="set"):
    mute_role = utils.get(ctx.guild.roles,id=int(args[0]))
    if (mute_role==None):
      return await ctx.send("I can't find this role:face_with_monocle:")
    gcursor.execute(f"""UPDATE guild SET mute_role={int(args[0])} WHERE id={ctx.guild.id}""")
    gconn.commit()
    await ctx.send(f"The mute role has been successfully set.\nName: **{mute_role.name}**\nID: **{mute_role.id}**\n<@&{mute_role.id}>")

@Bot.command()
async def say(ctx,*,msg):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  await ctx.message.delete()
  await ctx.send(msg)
  print(f"Bot said: {msg}")

@Bot.command()
@commands.has_permissions(administrator= True)
async def mute(ctx, member: discord.Member,*,reason=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  if member == ctx.message.author:
        return await ctx.send("You can't mute yourself.")
  if member == Bot.user:
    return await ctx.send("You can't mute me.")
  msgg =  f'**{ctx.message.author}** muted **{member}**. Reason: **{reason}**' if reason != None else f'**{ctx.message.author}** muted **{member}**.'
  msgdm = f"You were muted in **{ctx.guild.name}** Reason: **{reason}**." if reason != None else f'You were muted in **{ctx.guild.name}**.'
  for row in gcursor.execute(f"SELECT mute_role FROM guild WHERE id={ctx.guild.id}"):
    mute_role = utils.get(ctx.guild.roles,id=int(row[0]))
    if (mute_role==None):
      return await ctx.send("I can't find mute role:face_with_monocle:\nType `&muterole set [id]` to select it or `&muterole add [name]` to create one")
    if (mute_role in member.roles):
      return await ctx.send(f'**{member}** has already muted!')
    await member.add_roles(mute_role)
    await ctx.send(msgg)  
    if (not member.bot): 
      await member.send(msgdm)
  
@Bot.command()
@commands.has_permissions(administrator= True)
async def unmute(ctx, member: discord.Member):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  for row in gcursor.execute(f"SELECT mute_role FROM guild WHERE id={ctx.guild.id}"):
    mute_role = utils.get(ctx.guild.roles,id=int(row[0]))
    if (mute_role==None):
      return await ctx.send("I can't find mute role:face_with_monocle:\nType `&muterole set [id]` to select it or `&muterole add [name]` to create one")
    if (not mute_role in member.roles):
      return await ctx.send(f"This player not muted.")
    await ctx.send(f'**{ctx.message.author}** unmuted **{member}**.')
    await member.remove_roles(mute_role)

@Bot.command()
@commands.has_permissions(administrator= True)
async def kick(ctx, member : discord.User, *, reason=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
    if member == ctx.message.author:
        return await ctx.send("You can't kick yourself.")
    if member == Bot.user:
      return await ctx.send("You can't kick me.")
    msgg =  f'**{ctx.message.author}** kicked **{member}**. Reason: **{reason}**' if reason != None else f'**{ctx.message.author}** kicked **{member}**.'
    msgdm = f"You were kicked in **{ctx.guild.name}** Reason: **{reason}**." if reason != None else f'You were kicked in **{ctx.guild.name}**.' 
    await ctx.send(msgg)  
    if (not member.bot): 
      await member.send(msgdm)
    await ctx.guild.kick(member, reason=reason)

@Bot.command()
@commands.has_permissions(administrator= True)
async def ban(ctx, member : discord.User, *, reason=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
    if member == ctx.message.author:
        return await ctx.send("You cannot ban yourself.")
    if member == Bot.user:
      return await ctx.send("You cannot ban me.")
    msgg =  f'**{ctx.message.author}** banned **{member}**. Reason: **{reason}**.' if reason != None else f'**{ctx.message.author}** banned **{member}**.'
    msgdm = f'You were banned in **{ctx.guild.name}** Reason: **{reason}**.' if reason != None else f'You were banned in **{ctx.guild.name}**.'
    await ctx.send(msgg)  
    if (not member.bot): 
      await member.send(msgdm)
    await ctx.guild.ban(member, reason=reason)

@Bot.command()
@commands.has_permissions(administrator= True)
async def unban(ctx, arg=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
  if arg==None:
    await ctx.send(":hammer:Banned users:")
  for i in await ctx.guild.bans():
    if (arg==None):
      await ctx.send(f':no_mouth:**{i.user}**')
    if (str(i.user.id)==arg):
      await ctx.guild.unban(i.user)
      return await ctx.send(f'**{ctx.message.author}** unbanned **{i.user}**.')
    elif (str(i.user)==arg):
      await ctx.guild.unban(i.user)
      return await ctx.send(f'**{ctx.message.author}** unbanned **{i.user}**.')
    elif (not arg==None):
      return await ctx.send("I can't find this user:face_with_monocle:")
      

@Bot.command()
@commands.has_permissions(administrator= True)
async def tempban(ctx, member : discord.Member, time:int, arg:str, *, reason=None):
  if (not utils.get(ctx.guild.roles,name=luna_m) in ctx.message.author.roles):
    return await ctx.send(f':no_entry_sign:Acces deined! You need to have a "{luna_m}" role to do this!(You must create this role)')
    if member == ctx.message.author:
        return await ctx.send("You cannot ban yourself.")
    if member == Bot.user:
      return await ctx.send("You cannot ban me.")
    msgg =  f'**{ctx.message.author}** tempbanned **{member}**. Time: **{time}{arg}**, Reason: **{reason}**.' if reason != None else f'**{ctx.message.author}** tempbanned **{member}**. Time: **{time}{arg}**'
    msgdm = f'You were tempbanned in **{ctx.guild.name}**. Time: **{time}{arg}**, Reason: **{reason}**.' if reason != None else f'You were tempbanned in **{ctx.guild.name}**. Time: **{time}{arg}**'  
    await ctx.send(msgg)
    if (not member.bot): 
      await member.send(msgdm)
    await member.ban()
    if arg == "s":
        await asyncio.sleep(time)          
    elif arg == "m":
        await asyncio.sleep(time * 60)
    elif arg == "h":
        await asyncio.sleep(time * 60 * 60)
    elif arg == "d":
        await asyncio.sleep(time * 60 * 60 * 24)
    await member.unban()
    if (not member.bot): 
      await member.send(f'{member.mention}, you has been unbanned in **{ctx.guild.name}**!')

Bot.run('NzQxMTczOTM1NDA3NjI4MzI5.XyzuBA.SYmr6t2FPwMg7v-aRYOUmgxfpW0')