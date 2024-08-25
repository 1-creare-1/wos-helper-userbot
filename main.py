from dotenv import load_dotenv
import discum
import jellyfish
from fuzzywuzzy import fuzz

import re
import time
import os
import random

import issues

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

BLACKLIST_USERS = [
    "1121606226082533382", # self

    # "476057232186933274", # while true do
    "554717539935060028", # som because they hate userbots for some reason

    "260174728717664257", # Joe
    "672930748684173352", # Hexcede
    "410522966007480320", # Weldify

    "717916372734312538", # Angry Waffles
]

BLACKLIST_ROLES = [
    "617451786311041052", # Bot role
    "616089401562365967", # Developer
    "744775284703625317", # Discord Mod
    "1085775746460549200", # Testing Mod
]

EMOJIES = [
    "shh:879908104400146524",
    "carbonmonoxide:914605437163307089"
]

def on_hegced_ping(m):
    resp = get_response(m['content'], ignore_cooldown=True, update_cooldown=False)
    if resp and resp != on_hegced_ping:
        bot.reply(m['channel_id'], m['id'], "You probably meant to ping the real Hexcede however instead of doing that you should use <https://github.com/Eggs-D-Studios/wos-issues/issues> or <#1050351736243621948>")

RESPONSES = [
    # (['<@468384658653184040>'], 'goober :3'), # creare
    # (['<@672930748684173352>'], 'Hexcede is very busy and instead of bothering him you can ask questions in <#1050351736243621948> channel and report bugs in <https://github.com/Eggs-D-Studios/wos-issues/issues>'),
    ([r'<@672930748684173352>.*?fix'], "Pinging Hexcede is not the correct way to report a bug, please use <https://github.com/Eggs-D-Studios/wos-issues/issues>"),
    ([r'<@672930748684173352>.*?add'], "Please use <https://github.com/Eggs-D-Studios/wos-issues/issues> for suggestions"),
    ([r'<@672930748684173352>.*?how',r'<@672930748684173352>.*?why',r'<@672930748684173352>.*?\?'], "Please use <#1050351736243621948> for questions"),

    ([r'how.*?bug', r'report.*?bug', r'bug report', r'report bug', r'found bug'], 'You can report bugs [here](<https://github.com/Eggs-D-Studios/wos-issues/issues>)'),

    # FAQ from #faq chanel
    # (broken('blade'), "> Blades aren't broken, they require at least 10 studs per second of speed, and deal damage based on relative durability and speed, the model builder has a button for this, hammer tool has Modify\n\\-Hexcede"),
    (broken('blade'), "Blades don't currently appear to be working, the bug has already been reported"),
    (broken('button'), "> Buttons aren't broken, they are components, the model builder has a button for this\n\\-Hexcede"),
    (broken('door'), "> Doors are not removed, they are components, the model builder has a button for this, hammer tool has Modify\n\\-Hexcede"),
        ([r'blade.*?removed'], "Blades are not removed, they are components, the model builder has a button for this, hammer tool has Modify"),
    (broken('refin'), "> The refinery is not broken, the wire cache is (I said this would happen)\n\\-Hexcede"),
    (broken(r'power.*?cell'), "> PowerCells are not broken, the wire cache is (I said this would happen)\n\\-Hexcede"),
    (broken('warp')+broken('hyperdrive'), "> Warping is not broken, you configured the coordinates wrong or are not sitting in a seat\n\\-Hexcede"),
    (broken('teleport'), "> Teleporter is not broken, the hitbox was too high in the air and has been fixed\n\\-Hexcede"),
    (broken('heater'), "> Heaters are not broken, they are slow\n\\-Hexcede"),
    (broken('cooler'), "> Coolers are not broken, they are slow\n\\-Hexcede"),
    # (broken('hammer'), "> The hammer tool is not broken, it was fixed now\n\\-Hexcede"),
    (broken('hammer'), "Please notify joe with F9 logs and if possible a video of the bug happening"),
    (broken('extractor'), "> Extractor is not broken, configure your bin\n\\-Hexcede"),
    (broken('mb')+broken('model')+broken('builder')+broken('load'), "> The main model builder is not out of date, the staging model builder is out of date, use the main model builder for the main game now\n\\-Hexcede"),

    # ([r'void.*?ship',r'ship.*?void'], "> Ships were never voided they just didn't load, go visit the region they were in and they will be there\n\\-Hexcede"),
    ([r'warp.*?dupe',r'dupe.*?warp',r'hyperdrive.*?dupe',r'dupe.*?hyperdrive'], "> The initial warp duping bug was already fixed, the one that existed in the old game has also been fixed and has nothing to do with the initial warp dupe from immediately after wipe\n\\-Hexcede"),
    ([r'part shift',], "> Nothing you are seeing that you think is part shift is part shift, however there are issues with welds that I am aware of please stop pestering me about it\n\\-Hexcede"),
    (broken('thrust','\bion[\br]','rocket'), "> Nothing happened to Thrusters or IonRockets, they were updated to use the new Roblox constraints because the old ones literally crash the game because of a Roblox bug that I have zero control over\n\\-Hexcede"),
    ([r'heat.*?extract',r'extract.*?heat'], "> Extractors don't cool, the heat is just moving to where the items are due to legacy behaviour\n\\-Hexcede"),

    (['trigger antenna'], "This is a known bug, its due to generator buffer"),
    ([r'petrol.*?gas', r'gas.*?petrol'], "The bugs with refineries are already known."),
    ([r'boil.*?heat',r'heat.*?boil'], "Theres something funky going on with them. Placing an `AirSupply` super close to the boiler seems to fix the issue."),

    # Misc
    (['<@1121606226082533382>'], "Hello!\nI'm being developed by <@468384658653184040> to help answer very frequently asked questions. If you have a suggestion for a FAQ I should answer, just ping creare!"),
    (['ping[0-9]'], 'pong'),

    # silly
    (['<@476057232186933274>'], on_hegced_ping),
    ([':3'], lambda m: bot.addReaction(m['channel_id'], m['id'], "🐱")),

    # At bottom so it gets mached for last. Don't want the bot ignoring "bug" just so it can respond with an emoji lol
    (['\bbug'], lambda  m: bot.addReaction(m['channel_id'], m['id'], random.choice(EMOJIES))),
]

FOOTER = "\n-# This is an automated message and I have no affiliation with the developers or admins. My responses may not be 100% accurate.\n-# Most information is taken from <#1109343097596432434>, it is highly recommended to read everything in that channel."


def get_response(content: str, ignore_cooldown=False, update_cooldown=True):
    content = content.lower()
    content = re.sub("[^a-z0-9<@>? ]", "", content)
    for response in RESPONSES:
        if not ignore_cooldown and type(response[1]) is str and response[1] in last_response_time and time.time() - last_response_time[response[1]] < COOLDOWN_BETWEEN_UNIQUE_RESPONSES:
            continue
        for pattern in response[0]:
            if re.search(pattern, content):
                if update_cooldown:
                    last_response_time[response[1]] = time.time()
                return response[1]

bot = discum.Client(token=TOKEN, log=False)

# bot.sendMessage("659130771667156992", "turned on")

last_response_time = {}
github_issues = issues.get_all_new_issues()

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

        if m['author']['id'] in BLACKLIST_USERS:
            return
        
        for role in m['author']['roles']:
            if role in BLACKLIST_ROLES:
                return

        if guildID == SERVER:
            response = get_response(content)
            if response:
                print(f"Responding to {username} with {response}")
                if type(response) is str:
                    bot.reply(channelID, messageid, response+FOOTER, )
                else:
                    response(m)
            # elif m['author']['id'] == "468384658653184040" and channelID == "662095345366335518":
            else:
                cleaner_match = re.compile(r'[^a-z0-9 ]')
                def clean_string(string):
                    return re.sub(cleaner_match, "", string.lower())
                
                valid_words = set()
                for issue in github_issues:
                    for word in clean_string(issue['title']).split(" "):
                        valid_words.add(word)
                
                striped_content = list()
                for word in clean_string(content).split(" "):
                    if word in valid_words:
                        striped_content.append(word)
                striped_content = ' '.join(striped_content)

                # If no response, see if a github issue matches the users request
                best_match = None
                best_match_confidence = 0
                for issue in github_issues:

                    # zerothLabelName = labels[0]["name"]

                    # confidence = jellyfish.levenshtein_distance(content, issue['title'])
                    # confidence = 100 if content == issue['title'] else 0

                    issue_words = clean_string(issue['title']).split(" ")
                    request_words = striped_content.split(" ")

                    confidence = 0
                    matches = 0
                    for word in issue_words:
                        if word in request_words:
                            matches += 1
                            confidence += 1
                    percentThatMatched = matches/len(issue_words)
                    confidence *= percentThatMatched

                    # confidence = fuzz.ratio(clean_string(issue['title']), striped_content)

                    if confidence > best_match_confidence:
                        best_match = issue
                        best_match_confidence = confidence

                if best_match:
                    title = best_match['title']
                    link = best_match['html_url']
                    creator = best_match['user']['login']
                    labels = best_match['labels']
                
                    if best_match_confidence > 1:
                        print(f"{content} -> Citing issue {title} to {username}")
                        bot.reply(channelID, messageid, f"(#{best_match["number"]}) [{title}](<{link}>) by {creator} (confidence: {best_match_confidence})")
                    else:
                        print(f"{content} -> Not citing issue {title} to {username} becuase only {best_match_confidence} confidence")




        # print("> guild {} channel {} | {}#{}: {}".format(guildID, channelID, username, discriminator, content))

bot.gateway.run(auto_reconnect=True)

while True:
    time.sleep(60)
    github_issues = issues.get_all_new_issues()