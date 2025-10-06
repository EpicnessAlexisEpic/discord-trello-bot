# main.py
import os
import requests
import random
import time
from datetime import datetime, timedelta
import sys

# -----------------------------
# Configuration (env vars)
# -----------------------------
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# sanity check
missing = [name for name, val in [
    ("TRELLO_KEY", TRELLO_KEY),
    ("TRELLO_TOKEN", TRELLO_TOKEN),
    ("TRELLO_BOARD_ID", TRELLO_BOARD_ID),
    ("DISCORD_WEBHOOK", WEBHOOK_URL),
] if not val]
if missing:
    raise SystemExit(f"Missing environment variables: {', '.join(missing)}")

BOARD_URL = (
    f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    f"?cards=open&card_fields=name,labels,desc&checklists=all&fields=name"
    f"&key={TRELLO_KEY}&token={TRELLO_TOKEN}"
)

LAST_RUN_FILE = "last_run.txt"

# -----------------------------
# Dialogue lists (100 each)
# (copy-paste-ready; text/kaomoji emoticons)
# -----------------------------
intros = [
 "I just peeked at your board and I’m so excited to share what I found! :-)",
 "Hi Alex — I had a little look at your board and I’ve got news! =)",
 "Good news! I checked your Trello and want to tell you about it :D",
 "Hey — I looked over your board and I’m here to cheer you on ;-)",
 "Hello! I took a peek at your Trello and I’m excited to report back ;)",
 "Hi there! I checked your board and I’m smiling about it :P",
 "Oh hi! I looked at your board and found bits to celebrate XP",
 "Hey Alex — I peeked at your board and noted some things :3",
 "Hello! I popped by your Trello and it looks interesting ^_^",
 "Hi! I checked your board and I’m pleasantly surprised ^-^",
 "Hello Alex — I took a peek and wanted to give you an update ^^",
 "Hiya! I scanned your board and I’m ready to share the details (^_^)",
 "Hey! I had a look at your board and I’m excited to tell you (^.^)",
 "Hi Alex! I browsed your board and I’m smiling about it (＾▽＾)",
 "Hello! I checked your Trello and I’m happy to share (⌒‿⌒)",
 "Hey Alex — Sora here, I glanced at your board and I’m excited (⌒▽⌒)",
 "Hello! I popped in to see your Trello and I’m all smiles (◕‿◕)",
 "Hi Alex! I checked your lists and I’ve got some friendly notes (◠‿◠)",
 "Hey — I looked at your board and noticed lovely things (≧◡≦)",
 "Hello Alex! I checked your projects and I’m feeling cheerful (≧ω≦)",
 "Hi! I peeked at your Trello and I’m full of happy energy (✧ω✧)",
 "Hey Alex — I had a look at your board and I’m being supportive (´｡• ᵕ •｡`)",
 "Hello! I viewed your board and I’m ready to give a warm update ʘ‿ʘ",
 "Hi Alex — I checked your Trello and I’m feeling motivated for you (•̀ᴗ•́)",
 "Hey! I popped by your board and I’m excited to help out (•̀ᴗ•́)و",
 "Hello Alex! I peeked at your tasks and I’m ready to cheer (•̀ω•́)",
 "Hi! I looked through your board and I’m ready to encourage you (ง'̀-'́)ง",
 "Hey Alex — I glanced at your Trello and I’m rooting for you (ง^‿^)ง",
 "Hello! I checked your lists and I’m here with support (☞ﾟヮﾟ)☞",
 "Hi Alex! I browsed your Trello and I’m sending warm thoughts (｡◕‿◕｡)",
 "Hey! I looked at your board and I’m here to celebrate (ღ˘⌣˘ღ)",
 "Hello Alex — I checked your board and I’m excited to share (＾ω＾)",
 "Hi! I peeked at your Trello and I’ve got encouraging words (✿◠‿◠)",
 "Hey Alex — I visited your board and I’m happily reporting ʕ•ᴥ•ʔ",
 "Hello! I checked your Trello and I’m grinning for you (ᵔᴥᵔ)",
 "Hi Alex — I looked at your board and I’m hoping to inspire (ಥ‿ಥ)",
 "Hey! I checked your Trello and I’m quietly proud of you (ಥ_ಥ)",
 "Hello Alex — I peeked at your lists and I’m pleasantly surprised (◕ᴗ◕✿)",
 "Hi! I viewed your Trello and I’m full of gentle cheer (｡♥‿♥｡)",
 "Hey Alex — I checked your board and I’m delighted to tell you (✿╹◡╹)",
 "Hello! I took a peek at your Trello and I’m smiling inside (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
 "Hi Alex — I looked at your board and I’m excited to cheer (ﾉ◕‿◕)ﾉ",
 "Hey! I glanced at your Trello and I’m ready to encourage ٩(◕‿◕｡)۶",
 "Hello Alex — I checked your lists and I’m here to help (ヽ(•‿•)ノ)",
 "Hi! I took a look at your Trello and I’m excited to share (ヽ(*⌒∇⌒*)ﾉ)",
 "Hey Alex — I checked your board and I came with smiles (*^_^*)",
 "Hello! I looked at your Trello and I’m sending cheer ( ^_−)☆",
 "Hi Alex — I peeked at your tasks and I’m feeling upbeat (~‾▿‾)~",
 "Hey! I glanced at your Trello and I’m sending support (o^^)o",
 "Hello Alex — I checked your board and it warmed my heart (⌒▽⌒)☆",
 "Hi! I looked at your Trello and I’m excited for you (*≧ω≦)",
 "Hey Alex — I took a peek and I’ve got good vibes for you (ﾉ´ヮ`)ﾉ",
 "Hello! I peeked at your board and I’m smiling to share (*´꒳`*)",
 "Hi Alex — I checked your Trello and I’m full of cheer (=^_^=)",
 "Hey! I looked at your lists and I’m happy to report (^з^)-☆",
 "Hello Alex — I peeked at your projects and I’m excited (≧︶≦))",
 "Hi! I checked your Trello and I’ve got supportive words (^o^)/",
 "Hey Alex — I looked at your board and I’m glowing (＾◡＾)",
 "Hello! I peeked at your Trello and I couldn’t help but smile (￣▽￣)ノ",
 "Hi Alex — I checked your board and I’m cheering you on (°∀°)b",
 "Hey! I took a look at your Trello and I’m feeling lively (o^_^o)",
 "Hello Alex — I checked your board and I’m all encouragement (´ ▽｀)",
 "Hi! I peeked at your Trello and I’m sending a little pep (｀・ω・´)",
 "Hey Alex — I looked at your board and I’m quietly enthusiastic (︶ω︶)",
 "Hello! I checked your Trello and I’ve got warm words (✪ω✪)",
 "Hi Alex — I peeked at your lists and I’m happy to report (＾_＾;)",
 "Hey! I scanned your Trello and I’ve got a friendly update (´∇｀)",
 "Hello Alex — I looked at your board and I’m here for you (¬‿¬)",
 "Hi! I peeked at your Trello and I’m sending a little pep (°◡°♡)",
 "Hey Alex — I checked your lists and I’m smiling quietly (⌒_⌒;)",
 "Hello! I peeked at your Trello and I’ve got warm support (•◡•)/",
 "Hi Alex — I checked your board and I’m excited to tell you (´• ω •`)",
 "Hey! I glanced at your Trello and I’m cheerful for you (ﾉ◕ヮ◕)ﾉﾞ",
 "Hello Alex — I took a look at your board and I’m bubbling with cheer (ﾉ^_^)ﾉ",
 "Hi! I peeked at your board and I’m sending positive vibes ٩(＾◡＾)۶",
 "Hey Alex — I checked your Trello and I’m quietly proud (≧◡≦)/",
 "Hello! I looked at your board and I’m really glad to share (*ﾟ▽ﾟ*)",
 "Hi Alex — I peeked at your tasks and I’m hopeful for you (^人^)",
 "Hey! I checked your Trello and I’m glowing with encouragement (^_^)/~~",
 "Hello Alex — I glanced at your board and I’m ready to cheer (･_･ )",
 "Hi! I peered at your Trello and I’m sending a warm nudge (＾▽＾)V",
 "Hey Alex — I checked your board and I’m smiling inside (￣▽￣)",
 "Hello! I peeked at your Trello and I’m gently excited (°ロ°)☝",
 "Hi Alex — I checked your board and I’m happy to help (•ω•)",
 "Hey! I looked at your Trello and I’m pleasantly surprised (つ✧ω✧)つ",
 "Hello Alex — I peeked at your board and I’ve got nice things to say ( ´ ▽ ` )ﾉ",
 "Hi! I checked your Trello and I’m sending a supportive hug (づ｡◕‿‿◕｡)づ",
 "Hey Alex — I glanced through your lists and I’m encouraged (っ˘ω˘ς )",
 "Hello! I took a look at your Trello and I’m positively smiling (っ◔◡◔)っ",
 "Hi Alex — I skimmed your board and I’m here to cheer you on (❤ω❤)",
 "Hey! I peeked at your Trello and I’m brimming with support (*＾ω＾)人(＾ω＾*)",
 "Hello Alex — I checked your lists and I’m feeling glad (●´ω｀●)",
 "Hi! I popped by your Trello and I’m happy to report (＾▽＾)っ",
 "Hey Alex — I took a look and I’m rooting for you (¬_¬)",
 "Hello! I peeked at your board and I’ve got friendly news (￣︶￣)"
]

encouragements_done = [
 "Wow Alex, amazing progress — that’s brilliant! :-D",
 "Incredible work, Alex — you’re doing so well =D",
 "I’m so proud of you — keep shining! ;D",
 "Fantastic job, Alex — that’s worth celebrating ;)",
 "Beautiful progress — you’re on fire :P",
 "You crushed it — awesome job XP",
 "Absolutely lovely — well done :3",
 "So proud — your effort shows ^_^",
 "Terrific work — truly inspiring ^-^",
 "Stunning progress — keep it up ^^",
 "Exceptional — you really nailed it (^_^)",
 "Brilliant, Alex! Keep going (^.^)",
 "So impressive — you’re doing great (＾▽＾)",
 "Beautifully done — you make me smile (⌒‿⌒)",
 "Outstanding work — I’m so happy for you (⌒▽⌒)",
 "Great job — you deserve a pat on the back (◕‿◕)",
 "You’re amazing — terrific progress (◠‿◠)",
 "So good to see — your dedication shows (≧◡≦)",
 "Way to go — proud of you (≧ω≦)",
 "You’re on a roll — keep going (✧ω✧)",
 "Amazing effort — that really matters (´｡• ᵕ •｡`)",
 "That’s wonderful — I’m cheering for you ʘ‿ʘ",
 "Bravissimo — keep shining (•̀ᴗ•́)",
 "You did it — I’m celebrating with you (•̀ᴗ•́)و",
 "That’s a win — brilliant work (•̀ω•́)",
 "Nicely done — you’ve earned a smile (ง'̀-'́)ง",
 "Spectacular — you make progress look easy (ง^‿^)ง",
 "Amazing, Alex — keep the momentum (☞ﾟヮﾟ)☞",
 "Absolutely lovely — I’m beaming for you (｡◕‿◕｡)",
 "Wonderful job — you’re so capable (ღ˘⌣˘ღ)",
 "So proud — rock on (＾ω＾)",
 "Fantastic — you’re doing beautifully (✿◠‿◠)",
 "Great news — your effort is paying off ʕ•ᴥ•ʔ",
 "Incredible — very well done (ᵔᴥᵔ)",
 "Nice! That’s progress — keep going (ಥ‿ಥ)",
 "Blessings — you did a great job (ಥ_ಥ)",
 "Superb work — keep it steady (◕ᴗ◕✿)",
 "You did amazing — I’m proud (｡♥‿♥｡)",
 "Yes! That’s brilliant — well done (✿╹◡╹)",
 "Wonderful — that’s worth celebrating (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
 "You’re terrific — the results show (ﾉ◕‿◕)ﾉ",
 "Beautiful — you’re moving forward ٩(◕‿◕｡)۶",
 "Spectacular! Keep it up ヽ(•‿•)ノ",
 "That’s gorgeous progress — I adore it ヽ(*⌒∇⌒*)ﾉ",
 "So proud — your work shines (*^_^*)",
 "Excellent — perfect pace (^_−)☆",
 "Beautifully handled — bravo (~‾▿‾)~",
 "That’s so good — I’m cheering (o^^)o",
 "Hooray — that’s a lovely result (⌒▽⌒)☆",
 "Amazing job — keep the momentum (*≧ω≦)",
 "Thumbs up — you did great (ﾉ´ヮ`)ﾉ",
 "You’re doing splendidly — so happy (*´꒳`*)",
 "Wonderful — you finished this one (=^_^=)",
 "Yes! That’s so satisfying (^з^)-☆",
 "Top-notch work — outstanding (≧︶≦))",
 "Brilliant — you make me proud (^o^)/",
 "Incredible — on to the next (＾◡＾)",
 "Outstanding — you nailed it (￣▽￣)ノ",
 "So impressive — you shine (°∀°)b",
 "Beautiful — incredible effort (o^_^o)",
 "Marvelous — you’re doing so well (´ ▽｀)",
 "Wonderful — brilliant job (｀・ω・´)",
 "Awesome! Keep it up (︶ω︶)",
 "That’s lovely — keep going (✪ω✪)",
 "Amazing energy — so proud (＾_＾;)",
 "You did wonderfully — well done (´∇｀)",
 "You’re shining — keep pushing (¬‿¬)",
 "Stellar job — I’m impressed (°◡°♡)",
 "Terrific — you’re making me smile (⌒_⌒;)",
 "Fantastic — totally great (•◡•)/",
 "Beautiful finish — well done (´• ω •`)",
 "So happy — you finished it (ﾉ◕ヮ◕)ﾉﾞ",
 "Amazing — that’s real progress (ﾉ^_^)ﾉ",
 "You did it — bravo ٩(＾◡＾)۶",
 "Lovely result — keep going (≧◡≦)/",
 "Admirable — I adore this (*ﾟ▽ﾟ*)",
 "So proud — you’ve come far (^人^)",
 "Nice job — that’s wonderful (^_^)/~~",
 "That’s perfect — you did it (･_･ )",
 "Bravo — keep the good work (＾▽＾)V",
 "Fabulous — excellent outcome (￣▽￣)",
 "Wonderful — lovely job (°ロ°)☝",
 "You rocked it — great job (•ω•)",
 "That’s superb — I’m beaming (つ✧ω✧)つ",
 "So proud — well done ( ´ ▽ ` )ﾉ",
 "Amazing — I’m truly impressed (づ｡◕‿‿◕｡)づ",
 "Wonderful — you’re a star (っ˘ω˘ς )",
 "Brilliant — you deserve praise (っ◔◡◔)っ",
 "So great — keep the momentum (❤ω❤)",
 "Lovely — you did that so well (*＾ω＾)人(＾ω＾*)",
 "Exciting — that’s real progress (●´ω｀●)",
 "Beautiful — you finished strong (＾▽＾)っ",
 "Amazing — I love this (¬_¬)",
 "Stunning — excellent work (￣︶￣)"
]

encouragements_none = [
 "Hmm… it looks a bit quiet on progress today. Don’t worry — you’ve got this :)",
 "It’s okay if nothing moved today. Small steps tomorrow! :D",
 "No rush — we’ll make progress soon =)",
 "Don’t be hard on yourself — we can start small ;)",
 "It’s okay to rest — then tackle it again :P",
 "Sometimes no progress is prep — you’ll do great XP",
 "No worries — a fresh start tomorrow :3",
 "Take your time — we’ll try again ^_^",
 "No pressure — little by little ^-^",
 "It’s fine — every day is a chance ^^",
 "No stress — you’ll get there (^_^)",
 "It’s okay — tomorrow is another day (^.^)",
 "Rest is progress too (＾▽＾)",
 "Take a breath — we’ll try again (⌒‿⌒)",
 "No rush — steady wins (⌒▽⌒)",
 "All good — small things add up (◕‿◕)",
 "No worries — I believe in you (◠‿◠)",
 "It’s okay — we’ll make steps soon (≧◡≦)",
 "No pressure — gentle nudges help (≧ω≦)",
 "It’s fine — keep your head up (✧ω✧)",
 "Don’t worry — tomorrow is bright (´｡• ᵕ •｡`)",
 "It’s okay — we’ll start small ʘ‿ʘ",
 "Take it easy — you’ve got this (•̀ᴗ•́)",
 "We’ll try again tomorrow — no stress (•̀ᴗ•́)و",
 "It’s ok to pause — come back stronger (•̀ω•́)",
 "No pressure — baby steps are fine (ง'̀-'́)ง",
 "It’s alright — we’ll get moving soon (ง^‿^)ง",
 "No bother — rest up and try later (☞ﾟヮﾟ)☞",
 "It’s okay — even rest fuels progress (｡◕‿◕｡)",
 "Take care — tomorrow is new (ღ˘⌣˘ღ)",
 "It’s fine — recharge then go (＾ω＾)",
 "No rush — one step at a time (✿◠‿◠)",
 "Rest is important — we’ll do this soon ʕ•ᴥ•ʔ",
 "No worries — start small tomorrow (ᵔᴥᵔ)",
 "It’s okay — a short pause helps (ಥ‿ಥ)",
 "Rest today, progress tomorrow (ಥ_ಥ)",
 "Take it slow — I’m here for you (◕ᴗ◕✿)",
 "No pressure — small wins count (｡♥‿♥｡)",
 "It’s fine — breathe and reset (✿╹◡╹)",
 "No worries — we’ll get to it (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
 "It’s okay — gentle steps work (ﾉ◕‿◕)ﾉ",
 "No hurry — you’re still doing fine ٩(◕‿◕｡)۶",
 "Take your time — I believe in you ヽ(•‿•)ノ",
 "It’s okay — rest is progress ヽ(*⌒∇⌒*)ﾉ",
 "No problem — small steps tomorrow (*^_^*)",
 "It’s fine — we’ll try again later ( ^_−)☆",
 "Rest up — then we’ll tackle it (~‾▿‾)~",
 "No stress — tomorrow is fresh (o^^)o",
 "It’s okay — be kind to yourself (⌒▽⌒)☆",
 "Rest a bit — you’ll do fine (*≧ω≦)",
 "It’s all good — slow progress is fine (ﾉ´ヮ`)ﾉ",
 "Take it easy — I’m cheering ( *´꒳`*)",
 "No hurry — we’ll get there (=^_^=)",
 "It’s okay — small steps are progress (^з^)-☆",
 "Rest today — come back refreshed (≧︶≦))",
 "It’s fine — tomorrow is another chance (^o^)/",
 "Take a breather — I believe in you (＾◡＾)",
 "No pressure — take the pace you need (￣▽￣)ノ",
 "It’s okay — you’re still moving forward (°∀°)b",
 "Rest when needed — we’ll continue (o^_^o)",
 "No worries — approach gently (´ ▽｀)",
 "It’s okay — take care of yourself (｀・ω・´)",
 "No problem — we’ll make progress later (︶ω︶)",
 "Rest is okay — we’ll try again (✪ω✪)",
 "It’s fine — you’re allowed to pause (＾_＾;)",
 "No hurry — we’ll try again soon (´∇｀)",
 "It’s okay — small rest helps (¬‿¬)",
 "Take it slow — you have my support (°◡°♡)",
 "No rush — healing and rest matter (⌒_⌒;)",
 "It’s fine — I’m here, whenever you’re ready (•◡•)/",
 "Take care — you’ll find the drive again (´• ω •`)",
 "It’s okay — tomorrow may be better (ﾉ◕ヮ◕)ﾉﾞ",
 "Rest a bit — little steps tomorrow (ﾉ^_^)ﾉ",
 "It’s okay — a pause can spark momentum ٩(＾◡＾)۶",
 "No pressure — take your time (≧◡≦)/",
 "It’s fine — be gentle with yourself (*ﾟ▽ﾟ*)",
 "No worries — one day at a time (^人^)",
 "Take a break — you’ve earned it (^_^)/~~",
 "It’s okay — reset and restart (･_･ )",
 "Be kind to yourself — progress will come (＾▽＾)V",
 "No stress — tomorrow we try again (￣▽￣)",
 "It’s okay — every rest helps (°ロ°)☝",
 "Take care — I’m patient with you (•ω•)",
 "No rush — I’ll wait and cheer you on (つ✧ω✧)つ",
 "It’s fine — you’re still doing your best ( ´ ▽ ` )ﾉ",
 "Rest now — we’ll pick up later (づ｡◕‿‿◕｡)づ",
 "It’s okay — small and steady wins (っ˘ω˘ς )",
 "Take time — you are allowed to breathe (っ◔◡◔)っ",
 "No hurry — progress in your own time (❤ω❤)",
 "It’s okay — I trust your pace (*＾ω＾)人(＾ω＾*)",
 "Take a pause — then we’ll try (●´ω｀●)",
 "It’s fine — we’ll continue when you’re ready (＾▽＾)っ",
 "No pressure — you matter most (¬_¬)",
 "Rest kindly — come back refreshed (￣︶￣)"
]

endings = [
 "Here’s the full board so you can see everything and plan your next steps! (^-^)",
 "I’ve attached the full board below — ready for you to conquer it! (=^.^=)",
 "Take a look at the full board, Alex! Let’s keep moving forward! (＾ω＾)",
 "The full board is below — take your time and decide what to do next (^_−)☆",
 "I saved the full board for you — check it out when you’re ready (^-^*)",
 "Full report is attached — I believe in you! (^o^)",
 "See the full board below — we’ll tackle it together soon (^_^)/",
 "Full board is attached — you’ve got this! (￣︶￣)",
 "I left the full details in the file — take it slow and steady (･_･ )",
 "Full report is below — plan your next steps with love (*^_^*)",
 "I attached the board — enjoy reviewing it (＾▽＾)っ",
 "Full board’s attached — feel proud, Alex (´ ▽｀)",
 "I included the full details — you can do this (｀・ω・´)",
 "The board is attached — let’s keep moving forward (•◡•)/",
 "I’ve added the full board — take a peek when you can (｡◕‿◕｡)",
 "Full details are attached — breathe and decide (✿◠‿◠)",
 "I attached the full board — you’re not alone (ღ˘⌣˘ღ)",
 "Find full report attached — I’m cheering for you (´｡• ᵕ •｡`)",
 "Full board below — take a break, then tackle it (≧◡≦)",
 "I included everything in the file — plan at your pace (・_・)",
 "Full report is attached — you’re doing great (⌒‿⌒)",
 "I saved the full board for you — go through it gently (＾_＾)",
 "Full board attached — small steps win races (ﾉ◕ヮ◕)ﾉ",
 "See the full board — take the next tiny step (ﾉ´ヮ`)ﾉ",
 "Full report included — you’ve got my support (✧ω✧)",
 "I attached the board — check it whenever you’re ready (•̀ᴗ•́)",
 "Full details below — go at your own pace (•̀ω•́)",
 "I included the full report — you’ll do great (ง'̀-'́)ง",
 "Full board is attached — let’s make a plan soon (ง^‿^)ง",
 "I added the full board — review when calm (☞ﾟヮﾟ)☞",
 "Full report is below — you’re already doing well (｡◕‿◕｡)",
 "I attached the board — take your time with it (ღ˘⌣˘ღ)",
 "Full details included — make small steps (＾ω＾)",
 "I added the entire board — keep being awesome (✿╹◡╹)",
 "Full board attached — you’re stronger than you think (｡♥‿♥｡)",
 "I included the full file — take your next move (´∇｀)",
 "Full report is here — you got this, Alex (ﾉ◕‿◕)ﾉﾞ",
 "I attached everything — plan your next tiny win (ﾉ^_^)ﾉ",
 "Full board included — I’m rooting for you ٩(＾◡＾)۶",
 "File attached — go gently and succeed (≧◡≦)/",
 "Full report below — think small and act (●´ω｀●)",
 "I added the full board — look when you’re ready (っ˘ω˘ς )",
 "Full details attached — choose one small thing (っ◔◡◔)っ",
 "I included the board — take a deep breath first (＾▽＾)",
 "File attached — then we’ll tackle it (☆^_^)",
 "Full report is attached — plan with care (°◡°)",
 "I added the board — hope it helps you decide (¬_¬)",
 "Full file below — go at your pace (￣︶￣)",
 "I attached the full board — time to shine when ready (•‿•)",
 "Full report included — you know what to do next (＾_＾)",
 "I saved the full board — check it and act (^-^*)",
 "Full report attached — small steps, big wins (≧ω≦)",
 "I included everything — make a tiny plan (´｡• ᵕ •｡`)",
 "Full board attached — cheerfully yours (✿◠‿◠)",
 "I added the details — you can handle this (ღ˘⌣˘ღ)",
 "File attached — review and tackle one item (◕ᴗ◕✿)",
 "Full report below — you’re not alone (｡◕‿◕｡)",
 "I attached the board — go for it when ready (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
 "Full file attached — I believe in you (´∇｀)",
 "I saved your board — take a look and breathe (≧◡≦)",
 "Full report included — choose a tiny win (＾▽＾)っ",
 "I attached the board — you’ve got my support (❤ω❤)",
 "Full details below — plan one step (●´ω｀●)",
 "I included the board — you can do it (＾◡＾)",
 "Full file attached — I’m cheering (•‿•)",
 "I added the board — take one small action (^-^)",
 "Full report below — I’m here for you (＾ω＾)",
 "I attached everything — ready when you are (=^.^=)",
 "Full board is included — keep going gently (＾_＾)",
 "I added the full file — time for a tiny step (´• ω •`)",
 "Full report attached — you can accomplish this (●^o^●)",
 "I included the board — check and pick one task (°∀°)b",
 "Full file attached — you’re doing fine (^-^*)",
 "I saved the board — review and act (＾▽＾)V",
 "Full report included — focus on one thing (￣▽￣)",
 "I attached the full board — go slowly and win (･_･ )",
 "Full report below — you’ve got this, Alex (＾▽＾)",
 "I included the file — take your next step (￣︶￣)",
 "Full board attached — I’ll cheer you on (っ˘ω˘ς )",
 "I added the details — pick one and start (っ◔◡◔)っ",
 "Full report included — small step success (❤ω❤)",
 "I attached everything — time to shine (●´ω｀●)",
 "Full file below — choose a gentle goal (＾◡＾)",
 "I included the board — planning helps (＾_＾)",
 "Full report attached — go at your own pace (¬_¬)",
 "I saved the board — you have my support (≧◡≦)",
 "Full details included — tackle one small task (•‿•)",
 "I attached the board — make a gentle step (^-^)",
 "Full report below — I’m proud of you already (＾▽＾)",
 "I included the file — you can do it in pieces (￣︶￣)",
 "Full board attached — take a deep breath and choose (⋆‿⋆)",
 "I added the report — your next step awaits (♪^∇^)"
]

# -----------------------------
# Helper functions
# -----------------------------
def get_time_greeting():
    """Return time-aware greeting"""
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "Good morning, Alex! :)"
    elif 12 <= hour < 18:
        return "Good afternoon, Alex! (≧▽≦)"
    elif 18 <= hour < 22:
        return "Good evening, Alex! :]"
    else:
        return "Good night, Alex! (•‿•)"

def get_board_data():
    """Fetch lists + cards + checklists from Trello"""
    r = requests.get(BOARD_URL)
    r.raise_for_status()
    return r.json()

def get_priority_emoji(card):
    """Return short text emoji based on label keywords (few standard symbols)"""
    emojis = {
        "high": "!!",
        "medium": "!",
        "low": ".",
        "urgent": "!!!",
        "done": "✅"
    }
    if "labels" in card and card["labels"]:
        for label in card["labels"]:
            name = (label.get("name") or "").lower()
            for keyword, emoji in emojis.items():
                if keyword in name:
                    return emoji
    return ":"  # default small text marker

def sora_summary(total_lists, total_cards, completed_cards, total_items, completed_items):
    """Construct the Sora-style summary message"""
    time_greeting = get_time_greeting()
    intro = random.choice(intros)
    ending = random.choice(endings)

    total_possible = total_cards + total_items
    progress_ratio = (completed_cards + completed_items) / total_possible if total_possible > 0 else 0

    if progress_ratio == 0:
        encouragement = random.choice(encouragements_none)
    elif progress_ratio < 0.5:
        encouragement = "You're doing okay, Alex! Keep pushing, I believe in you! :)"
    else:
        encouragement = random.choice(encouragements_done)

    text = (
        f"{time_greeting}\n\n"
        f"{intro}\n\n"
        f"You have {total_lists} lists on your board.\n"
        f"{total_cards} cards total — {completed_cards} completed ✅\n"
        f"{total_items} checklist items — {completed_items} completed ✅\n\n"
        f"{encouragement}\n\n"
        f"{ending}\n\n"
        f"Here’s the full board so you can see everything:"
    )
    return text

def generate_report(board_data):
    """Generate full .txt report and summary counts"""
    lines = []
    total_cards = 0
    completed_cards = 0
    total_checklist_items = 0
    completed_checklist_items = 0

    for lst in board_data:
        list_name = lst.get("name", "Unnamed list")
        lines.append(f"📋 {list_name}")
        lines.append("")

        for card in lst.get("cards", []):
            card_name = card.get("name", "Untitled card")
            emoji = get_priority_emoji(card)

            # Gather checklist items for this card
            checklist_items = []
            for cl in card.get("checklists", []):
                for it in cl.get("checkItems", []):
                    checklist_items.append(it)

            if checklist_items:
                completed_items_count = sum(1 for it in checklist_items if it.get("state") == "complete")
                card_done = (completed_items_count == len(checklist_items))
            else:
                completed_items_count = 0
                card_done = False

            card_status = "✅" if card_done else "❌"
            lines.append(f"├─ {emoji} {card_name} - {card_status}")
            total_cards += 1
            if card_done:
                completed_cards += 1

            # Add per-checklist sections (preserve checklist names)
            for cl in card.get("checklists", []):
                cl_name = cl.get("name", "Checklist")
                lines.append(f"│   📑 {cl_name}:")
                for item in cl.get("checkItems", []):
                    item_name = item.get("name", "")
                    item_status = "✅" if item.get("state") == "complete" else "❌"
                    lines.append(f"│   ├─ {item_name} - {item_status}")
                    total_checklist_items += 1
                    if item.get("state") == "complete":
                        completed_checklist_items += 1

            # Per-card Sora commentary (use simple tailored lines)
            if card_done:
                # praise line - pick from encouragements_done but short
                praise = random.choice([
                    "Yay! You finished this one :] Great job, Alex! (≧▽≦)",
                    "Nice! This one is done — wonderful work! :)",
                    "Amazing — you completed it, Alex! :]",
                    "Nice finishing touch — well done! (•‿•)"
                ])
                lines.append(f"│   Note from Sora: {praise}")
            else:
                pep = random.choice([
                    "Keep going, Alex! You got this! :)",
                    "A little push and this will be done — believe in you! :]",
                    "You can do it — take it one step at a time (•‿•)",
                    "Stay steady, Alex — small steps win the race (≧▽≦)"
                ])
                lines.append(f"│   Note from Sora: {pep}")

            lines.append("")  # spacing between cards
        lines.append("")  # spacing between lists

    report_text = "\n".join(lines)
    short_summary = sora_summary(
        len(board_data),
        total_cards,
        completed_cards,
        total_checklist_items,
        completed_checklist_items
    )
    return report_text, short_summary

def send_to_discord_file(report_text, summary):
    """Send summary text then send the .txt file via webhook"""
    # Send summary message (text)
    post = requests.post(WEBHOOK_URL, json={"content": summary})
    post.raise_for_status()

    # Write file
    with open("trello_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    # Send file
    with open("trello_report.txt", "rb") as f:
        r = requests.post(WEBHOOK_URL, files={"file": f})
        r.raise_for_status()

# -----------------------------
# Main: progressive probability + random delay
# -----------------------------
def read_last_run():
    if os.path.exists(LAST_RUN_FILE):
        try:
            with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
                txt = f.read().strip()
                return datetime.strptime(txt, "%Y-%m-%d").date()
        except Exception:
            return None
    return None

def write_last_run(date_obj):
    with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
        f.write(date_obj.strftime("%Y-%m-%d"))

if __name__ == "__main__":
    # Determine days since last run
    last_run_date = read_last_run()
    today = datetime.now().date()
    if last_run_date:
        days_since_last = (today - last_run_date).days
    else:
        # if never run before, set to 1 day to allow reasonable chance to run
        days_since_last = 1

    # Progressive chance: base + (0.15 * days since last), capped
    base_chance = 0.2  # 20% base
    progressive_chance = min(base_chance + 0.15 * days_since_last, 0.9)  # cap at 90%
    print(f"[Sora] Days since last: {days_since_last}, chance to run today: {progressive_chance:.2f}")

    # Decide whether to run today
    if random.random() >= progressive_chance:
        print("[Sora] Taking a rest today :) No report sent.")
        sys.exit(0)

    # If we decided to run, add a random 0-4 hour delay so timing is unpredictable
    delay_seconds = random.randint(0, 4 * 3600)
    hrs = delay_seconds // 3600
    mins = (delay_seconds % 3600) // 60
    print(f"[Sora] Waiting {hrs} hours and {mins} minutes before sending...")
    time.sleep(delay_seconds)

    # Fetch Trello data and generate report
    try:
        board_data = get_board_data()
    except Exception as e:
        print("[Sora] Failed to fetch Trello board:", e)
        sys.exit(1)

    report_text, summary = generate_report(board_data)

    # Send to Discord
    try:
        send_to_discord_file(report_text, summary)
        print("[Sora] Report sent successfully!")
        # update last run
        write_last_run(today)
    except Exception as e:
        print("[Sora] Failed to send report:", e)
        sys.exit(1)