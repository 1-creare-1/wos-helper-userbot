from dotenv import load_dotenv
import discum
import re
import time
import os
import random

load_dotenv()

TOKEN = os.getenv('TOKEN')
SERVER = '616089055532417036'

COOLDOWN_BETWEEN_UNIQUE_RESPONSES = 30

def broken(*objects):
    out = []
    for object in objects:
        out += [
            f'{object}.*?work',
            f'{object}.*?broken',
            f'{object}.*?not',
            f'{object}.*?wrong',
            f'{object}.*?anymore',
            f"why.*?{object}"
        ]
    return out

EMOJIES = [
    "shh:879908104400146524",
    "carbonmonoxide:914605437163307089"
]

RESPONSES = [
    # (['<@468384658653184040>'], 'goober :3'), # creare
    # (['<@672930748684173352>'], 'Hexcede is very busy and instead of bothering him you can ask questions in <#1050351736243621948> channel and report bugs in https://github.com/Eggs-D-Studios/wos-issues/issues'),
    ([r'<@672930748684173352>.*?fix'], "Pinging Hexcede is not the correct way to report a bug, please use https://github.com/Eggs-D-Studios/wos-issues/issues"),
    ([r'<@672930748684173352>.*?add'], "Please use https://github.com/Eggs-D-Studios/wos-issues/issues for suggestions"),

    ([r'how.*?bug', r'report.*?bug', r'bug report', r'report bug', r'found bug'], 'You can report bugs [here](https://github.com/Eggs-D-Studios/wos-issues/issues)'),
    (['ping'], 'pong'),

    # FAQ from #faq chanel
    (broken('blade'), "> Blades aren't broken, they require at least 10 studs per second of speed, and deal damage based on relative durability and speed, the model builder has a button for this, hammer tool has Modify\n\\-Hexcede"),
    (broken('button'), "> Buttons aren't broken, they are components, the model builder has a button for this\n\\-Hexcede"),
    (broken('door'), "> Doors are not removed, they are components, the model builder has a button for this, hammer tool has Modify\n\\-Hexcede"),
    (broken('refin'), "> The refinery is not broken, the wire cache is (I said this would happen)\n\\-Hexcede"),
    (broken(r'power.*?cell'), "> PowerCells are not broken, the wire cache is (I said this would happen)\n\\-Hexcede"),
    (broken('warp')+broken('hyperdrive'), "> Warping is not broken, you configured the coordinates wrong or are not sitting in a seat\n\\-Hexcede"),
    (broken('teleport'), "> Teleporter is not broken, the hitbox was too high in the air and has been fixed\n\\-Hexcede"),
    (broken('heater'), "> Heaters are not broken, they are slow\n\\-Hexcede"),
    (broken('cooler'), "> Coolers are not broken, they are slow\n\\-Hexcede"),
    (broken('hammer'), "> The hammer tool is not broken, it was fixed now\n\\-Hexcede"),
    (broken('extractor'), "> Extractor is not broken, configure your bin\n\\-Hexcede"),
    (broken('mb')+broken('model')+broken('builder')+broken('load'), "> The main model builder is not out of date, the staging model builder is out of date, use the main model builder for the main game now\n\\-Hexcede"),

    ([r'void.*?ship',r'ship.*?void'], "> Ships were never voided they just didn't load, go visit the region they were in and they will be there\n\\-Hexcede"),
    ([r'warp.*?dupe',r'dupe.*?warp',r'hyperdrive.*?dupe',r'dupe.*?hyperdrive'], "> The initial warp duping bug was already fixed, the one that existed in the old game has also been fixed and has nothing to do with the initial warp dupe from immediately after wipe\n\\-Hexcede"),
    ([r'part shift',], "> Nothing you are seeing that you think is part shift is part shift, however there are issues with welds that I am aware of please stop pestering me about it\n\\-Hexcede"),
    (broken('thrust','ion','rocket'), "> Nothing happened to Thrusters or IonRockets, they were updated to use the new Roblox constraints because the old ones literally crash the game because of a Roblox bug that I have zero control over\n\\-Hexcede"),
    ([r'heat.*?extract',r'extract.*?heat'], "> Extractors don't cool, the heat is just moving to where the items are due to legacy behaviour\n\\-Hexcede"),

    # silly
    (['bug'], lambda channel, message: bot.addReaction(channel, message, random.choice(EMOJIES))),
]

FOOTER = "\n-# This is an automated message and I have no affiliation with the developers or admins. My responses may not be 100% accurate."

bot = discum.Client(token=TOKEN, log=False)

# bot.sendMessage("659130771667156992", "turned on")

last_response_time = {}

@bot.gateway.command
def helloworld(resp):
    if resp.event.ready_supplemental: #ready_supplemental is sent after ready
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(user['username'], user['discriminator']))
    if resp.event.message:
        m = resp.parsed.auto()
        guildID = m['guild_id'] if 'guild_id' in m else None #because DMs are technically channels too
        channelID = m['channel_id']
        username = m['author']['username']
        discriminator = m['author']['discriminator']
        content = m['content']
        messageid = m['id']

        if guildID == SERVER:
            for response in RESPONSES:
                if type(response[1]) is str and response[1] in last_response_time and time.time() - last_response_time[response[1]] < COOLDOWN_BETWEEN_UNIQUE_RESPONSES:
                    continue
                for pattern in response[0]:
                    if re.search(pattern, content.lower()):
                        last_response_time[response[1]] = time.time()
                        print(f"Responding to {m['author']['username']}")

                        if type(response[1]) is str:
                            bot.reply(channelID, messageid, response[1]+FOOTER)
                        else:
                            response[1](channelID, messageid)
                        
                        # Prevent multiple of the same response if multiple matches
                        break
        # print("> guild {} channel {} | {}#{}: {}".format(guildID, channelID, username, discriminator, content))

bot.gateway.run(auto_reconnect=True)