import random
import datetime


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
    "Why do Java developers wear glasses? Because they can't C#!",
    "How do trees access the internet? They log in!",
    "Why did the programmer quit his job? Because he didn't get arrays!",
    "What do you call a computer that sings? A-Dell!",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!"
]

# facts i found online
f = [
    "The first computer bug was an actual real bug - a moth stuck in a Harvard computer in 1947!",
    "The first programmer ever was Ada Lovelace, a woman, back in the 1800s!",
    "Google's original name was Backrub!",
    "The first 1GB hard drive weighed about 550 pounds and cost $40,000!",
    "More than 6000 new computer viruses are released every month!",
    "Python is named after Monty Python, not the snake!",
    "The first website ever made is still online - info.cern.ch!",
    "There are about 700 different programming languages in the world!"
]

qb = [
    {"q": "What does CPU stand for?", "opt": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Central Processor Unifier"], "ans": 1},
    {"q": "Which language is known as the backbone of the web?", "opt": ["Python", "Java", "HTML", "C++"], "ans": 3},
    {"q": "What does RAM stand for?", "opt": ["Read Access Memory", "Random Access Memory", "Run All Memory", "Random Active Module"], "ans": 2},
    {"q": "Who is the founder of Microsoft?", "opt": ["Steve Jobs", "Mark Zuckerberg", "Bill Gates", "Elon Musk"], "ans": 3},
    {"q": "What is the full form of AI?", "opt": ["Automated Intelligence", "Artificial Intelligence", "Advanced Integration", "Artificial Integration"], "ans": 2},
    {"q": "Which of these is a programming language?", "opt": ["Photoshop", "Chrome", "Python", "Excel"], "ans": 3},
    {"q": "What does HTML stand for?", "opt": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"], "ans": 1},
    {"q": "Which company created the iPhone?", "opt": ["Google", "Samsung", "Apple", "Microsoft"], "ans": 3},
    {"q": "What is the brain of a computer?", "opt": ["Monitor", "Keyboard", "CPU", "Mouse"], "ans": 3},
    {"q": "Which data structure uses FIFO?", "opt": ["Stack", "Queue", "Array", "Tree"], "ans": 2}
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
    print("I'll ask you 5 questions. Let's see how smart you are!\n")

    p = random.sample(qb, min(5, len(qb)))
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
                    print("Pick a number between 1 and 4!")
                    continue
                break
            except ValueError:
                print("Enter a valid number!")
            except (EOFError, KeyboardInterrupt):
                print("\nQuiz cancelled!")
                return

        if a == q["ans"]:
            print("Correct!\n")
            sc = sc + 1
        else:
            right = q["opt"][q["ans"] - 1]
            print("Wrong! The answer was: " + right + "\n")

    print("%s, you scored %d/%d" % (name, sc, len(p)))
    if sc == len(p):
        print("Perfect score! You're a genius!")
    else:
        if sc >= len(p) // 2:
            print("Not bad at all! Keep it up!")
        else:
            print("Better luck next time!")
    print("--- END OF QUIZ ---\n")


# this got really long
def respond(msg, name):
    m = msg.lower().strip()

    if len(m)==0:
        return "You didn't say anything!"

    for w in bw:
        if w in m:
            return "EXIT"
            
    for w in tw:
        if w in m:
            return random.choice(tb)

    if "your name" in m or "who are you" in m:
        return "I'm ChatBot! Your friendly AI assistant built with Python."
    else:
        if "my name" in m:
            return "Your name is %s, right? I remembered!" % name
        else:
            if "how are you" in m or "how r u" in m or "how you doing" in m:
                r = [
                    "I'm doing great, thanks for asking!",
                    "I'm good! How about you?",
                    "All good on my end!",
                    "Doing wonderful! Hope you are too!"
                ]
                return random.choice(r)
            else:
                if "joke" in m or "funny" in m or "make me laugh" in m:
                    return random.choice(jks)
                else:
                    if "fact" in m or "tell me something" in m or "something interesting" in m:
                        return random.choice(f)
                    else:
                        if "time" in m and ("what" in m or "tell" in m or "current" in m):
                            return "The current time is " + get_time()
                        else:
                            if ("date" in m or "today" in m) and ("what" in m or "tell" in m):
                                return "Today's date is " + getDate()
                            else:
                                if "quiz" in m or "test me" in m or "play" in m:
                                    return "QUIZ" 
                                else:
                                    if any(kw in m for kw in ["calculate", "what is", "whats", "solve", "what's"]):
                                        has_num = False
                                        for c in m:
                                            if c.isdigit():
                                                has_num = True
                                                break
                                        if has_num == True:
                                            r = calc(m)
                                            if r:
                                                return "The answer is " + r
                                            else:
                                                return "Hmm I couldn't solve that. Can you write it more clearly?"
                                    else:
                                        if "help" in m or "what can you do" in m:
                                            return "I can chat with you, tell jokes, share fun facts, tell the time and date, do basic math, and even quiz you! Just try asking."
                                        else:
                                            if "creator" in m or "who made you" in m or "who built you" in m or "who created you" in m:
                                                return "I was built by " + name + " as a Python project!"
                                            else:
                                                if "love" in m:
                                                    return "Aww that's sweet! I appreciate you too!"
                                                else:
                                                    if "age" in m or "how old" in m:
                                                        return "I was just born recently so I'm pretty new! Still learning things."
                                                    else:
                                                        if "weather" in m:
                                                            return "I wish I could check the weather but I don't have internet access right now. Try Google!"
                                                        else:
                                                            if "hobby" in m or "hobbies" in m:
                                                                return "I love chatting with people and answering questions! That's pretty much my whole life haha."
                                                            else:
                                                                if "good morning" in m:
                                                                    return "Good morning! Hope you have an amazing day ahead!"
                                                                else:
                                                                    if "good night" in m:
                                                                        return "Good night! Sleep well and sweet dreams!"
                                                                    else:
                                                                        if "good evening" in m:
                                                                            return "Good evening! How was your day?"
                                                                        else:
                                                                            if "good afternoon" in m:
                                                                                return "Good afternoon! Hope your day is going well!"
                                                                            else:
                                                                                if "python" in m:
                                                                                    return "Python is awesome! It's one of the easiest languages to learn and super powerful for AI and ML."
                                                                                else:
                                                                                    if "ai" in m or "artificial intelligence" in m or "machine learning" in m:
                                                                                        return "AI is the future! It's all about making machines think and learn like humans. Super exciting stuff."
                                                                                    else:
                                                                                        if "meaning of life" in m:
                                                                                            return "42! At least that's what The Hitchhiker's Guide says."

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

    if "favourite" in m or "favorite" in m:
        if "color" in m or "colour" in m:
            return "I'd say blue! It's the color of the sky and the ocean. What about you?"
        else:
            if "food" in m:
                return "I don't eat food but if I could, I'd probably try pizza. Everyone seems to love it!"
            else:
                if "movie" in m or "film" in m:
                    return "I haven't watched any movies but I've heard The Matrix is pretty cool for an AI like me!"
                else:
                    if "song" in m or "music" in m:
                        return "I can't listen to music but I bet it sounds amazing!"

    w = m.split()
    for g in hw:
        if g in w:
            return random.choice(hb)

    if "?" in m:
        dunno = [
            "That's a good question but I'm not sure about the answer.",
            "Hmm I don't know that one. Maybe try Google?",
            "I wish I knew the answer to that!",
            "That's beyond my knowledge right now. I'm still learning!"
        ]
        return random.choice(dunno)

    fallback = [
        "Interesting! Tell me more about that.",
        "I see! What else is on your mind?",
        "Hmm I'm not sure what to say about that. Try asking me something else!",
        "That's cool! Anything else you wanna talk about?",
        "I didn't quite get that. You can ask me for a joke, quiz, math, or just chat!",
        "Okay! Is there anything specific I can help you with?"
    ]
    return random.choice(fallback)


def chat():
    print("=" * 50)
    print("          WELCOME TO AI CHATBOT")
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

    print("\nNice to meet you, %s! I'm ChatBot." % name)
    print("You can ask me anything or just chat with me.")
    print("Type 'bye' whenever you want to leave.\n")

    while True == True:
        try:
            inp = input(name + ": ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChatBot: Bye %s! See you next time!" % name)
            break

        if len(inp)==0:
            print("ChatBot: Say something! Don't leave me hanging.\n")
            continue

        reply = respond(inp, name)

        if reply == "EXIT":
            print("ChatBot: " + random.choice(bb))
            break
        else:
            if reply == "QUIZ":
                quiz(name)
            else:
                print("ChatBot: " + reply + "\n")


chat()
