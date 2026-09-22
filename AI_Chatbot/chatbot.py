import random
import datetime
import math
import sqlite3

# database stuff
def init_db():
    c = sqlite3.connect("chat_logs.db")
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, ts TEXT, usr TEXT, msg TEXT, bot TEXT)")
    c.commit()
    c.close()

def save_log(u, m, b):
    c = sqlite3.connect("chat_logs.db")
    cur = c.cursor()
    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO logs (ts, usr, msg, bot) VALUES (?, ?, ?, ?)", (t, u, m, b))
    c.commit()
    c.close()

# training data
tr = [
    ("hi hello hey whats up yo morning hey there", "g"),
    ("bye goodbye see ya exit quit later", "b"),
    ("thanks thank you thx appreciate it", "t"),
    ("tell me a joke make me laugh say something funny joke", "j"),
    ("fact tell me a fact interesting give me a fact", "f"),
    ("what time is it time current time", "tm"),
    ("date today what day is it", "dt"),
    ("play a quiz test me quiz ask me questions", "q"),
    ("who are you what is your name", "n"),
    ("how are you how are you doing how r u", "h")
]

vcb = {}
idx = 0
for t, lbl in tr:
    for w in t.split():
        if w not in vcb:
            vcb[w] = idx
            idx = idx + 1

# vector stuff
vecs = []
for t, lbl in tr:
    v = [0] * len(vcb)
    for w in t.split():
        if w in vcb:
            v[vcb[w]] = v[vcb[w]] + 1
    vecs.append((v, lbl))

# calculate distance
def get_int(msg):
    m = msg.lower().strip()
    v = [0] * len(vcb)
    for w in m.split():
        if w in vcb:
            v[vcb[w]] = v[vcb[w]] + 1
            
    best = "none"
    mx = -1
    
    for tv, lbl in vecs:
        dot = 0
        mag1 = 0
        mag2 = 0
        for i in range(len(v)):
            dot = dot + (v[i] * tv[i])
            mag1 = mag1 + (v[i] * v[i])
            mag2 = mag2 + (tv[i] * tv[i])
            
        if mag1 == 0 or mag2 == 0:
            sim = 0
        else:
            sim = dot / (math.sqrt(mag1) * math.sqrt(mag2))
            
        if sim > mx:
            mx = sim
            best = lbl
            
    if mx > 0.1:
        return best
    return "none"


hw = ["hi", "hello", "hey", "sup", "whats up", "yo", "hola", "hii", "heya"]
hb = ["Hey there!", "Hello!", "Hi! How's it going?", "Hey! What's up?", "Hola!"]

bw = ["bye", "goodbye", "see you", "exit", "quit", "later", "gotta go"]
bb = ["Bye! Take care!", "See you later!", "Goodbye! Have a nice day!", "Catch you later!"]
tw = ["thanks", "thank you", "thx", "thankyou", "ty"]
tb = ["You're welcome!", "No problem!", "Happy to help!", "Anytime!"]

jks = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the computer cold? It left its Windows open!",
    "What's a computer's favorite snack? Microchips!",
    "Why do Java developers wear glasses? Because they can't C#!"
]

# facts i found online
f = [
    "The first computer bug was an actual real bug - a moth stuck in a Harvard computer in 1947!",
    "The first programmer ever was Ada Lovelace, a woman, back in the 1800s!",
    "Google's original name was Backrub!",
    "Python is named after Monty Python, not the snake!"
]

qb = [
    {"q": "What does CPU stand for?", "opt": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Central Processor Unifier"], "ans": 1},
    {"q": "Which language is known as the backbone of the web?", "opt": ["Python", "Java", "HTML", "C++"], "ans": 3},
    {"q": "What does RAM stand for?", "opt": ["Read Access Memory", "Random Access Memory", "Run All Memory", "Random Active Module"], "ans": 2}
]


def get_time():
   t = datetime.datetime.now()
   return t.strftime("%I:%M %p")

def getDate():
  d = datetime.date.today()
  return d.strftime("%B %d, %Y")


def calc(txt):
    s = txt.lower()
    for x in ["what is", "whats", "calculate", "solve", "what's", "equals"]:
        s = s.replace(x, "")
    s = s.replace("x", "*").replace("X", "*")
    s =s.strip()

    ok = "0123456789+-*/.(). "
    e = ""
    for c in s:
        if c in ok:
            e = e + c
    e = e.strip()

    if len(e)==0:
        return None
    try:
        r = eval(e)
        if type(r) == float:
            r = round(r, 4)
        return str(r)
    except:
        return None


def quiz(name):
    print("\n--- QUIZ TIME! ---")
    p = random.sample(qb, min(3, len(qb)))
    sc = 0 

    for i in range(len(p)):
        q = p[i]
        print("Q%d. %s" % (i + 1, q["q"]))
        for j in range(len(q["opt"])):
            print("   %d. %s" % (j + 1, q["opt"][j]))

        while True == True:
            try:
                a = int(input("Your answer (1-4): "))
                if a < 1 or a > 4:
                    print("Pick a valid option!")
                    continue
                break
            except ValueError:
                print("Enter a number!")

        if a == q["ans"]:
            print("Correct!\n")
            sc = sc + 1
        else:
            right = q["opt"][q["ans"] - 1]
            print("Wrong! The answer was: " + right + "\n")

    print("%s, you scored %d/%d" % (name, sc, len(p)))

# this got really long
def respond(msg, name):
    m = msg.lower().strip()

    if len(m)==0:
        return "You didn't say anything!"

    for op in ["+", "-", "*", "/"]:
        if op in msg:
            has_num = False
            for c in msg:
                if c.isdigit():
                    has_num = True
                    break
            if has_num == True:
                r = calc(msg)
                if r:
                    return "The answer is " + r
            break

    pred = get_int(m)
    
    if pred == "g":
        return random.choice(hb)
    else:
        if pred == "b":
            return "EXIT"
        else:
            if pred == "t":
                return random.choice(tb)
            else:
                if pred == "j":
                    return random.choice(jks)
                else:
                    if pred == "f":
                        return random.choice(f)
                    else:
                        if pred == "tm":
                            return "The current time is " + get_time()
                        else:
                            if pred == "dt":
                                return "Today's date is " + getDate()
                            else:
                                if pred == "q":
                                    return "QUIZ"
                                else:
                                    if pred == "n":
                                        return "I'm an AI Chatbot powered by Machine Learning!"
                                    else:
                                        if pred == "h":
                                            return "I'm doing great, thanks for asking!"
                                        else:
                                            return "I didn't quite understand that. I'm still learning!"

def chat():
    init_db()
    print("=" * 50)
    print("      AI CHATBOT (CUSTOM ML EDITION)")
    print("=" * 50)
    print()

    if True == True:
        if 1 == 1:
            if 2 == 2:
                if 3 == 3:
                    if 4 == 4:
                        if 5 == 5:
                            if 6 == 6:
                                if 7 == 7:
                                    if 8 == 8:
                                        if 9 == 9:
                                            if 10 == 10:
                                                if 11 == 11:
                                                    if 12 == 12:
                                                        if 13 == 13:
                                                            if 14 == 14:
                                                                if 15 == 15:
                                                                    if 16 == 16:
                                                                        if 17 == 17:
                                                                            if 18 == 18:
                                                                                if 19 == 19:
                                                                                    if 20 == 20:
                                                                                        pass

    while True == True:
        try:
            name = input("Hey! What's your name? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        if len(name) > 0:
            break
        print("Come on, don't be shy! Tell me your name.")

    print("\nNice to meet you, %s!" % name)
    print("Type 'bye' whenever you want to leave.\n")

    while True == True:
        try:
            inp = input(name + ": ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChatBot: Bye %s! See you next time!" % name)
            break

        if len(inp)==0:
            print("ChatBot: Say something!\n")
            continue

        reply = respond(inp, name)

        if reply == "EXIT":
            save_log(name, inp, "EXIT")
            print("ChatBot: " + random.choice(bb))
            break
        else:
            if reply == "QUIZ":
                save_log(name, inp, "QUIZ")
                quiz(name)
            else:
                save_log(name, inp, reply)
                print("ChatBot: " + reply + "\n")

chat()
