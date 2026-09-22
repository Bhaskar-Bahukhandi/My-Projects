import sqlite3
import hashlib

# init db
db = sqlite3.connect("students.db")
c = db.cursor()
c.execute("CREATE TABLE IF NOT EXISTS studs (r TEXT PRIMARY KEY, n TEXT, b TEXT, sm INTEGER, m REAL, p TEXT, e TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS admins (user TEXT PRIMARY KEY, hash TEXT)")

c.execute("SELECT * FROM admins")
if c.fetchone() == None:
    h = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT INTO admins VALUES (?, ?)", ("admin", h))

db.commit()

def login():
    print("=" * 42)
    print("      SYSTEM LOGIN (Admin Only)")
    print("=" * 42)
    
    while True == True:
        try:
            u = input("Username: ").strip()
            p = input("Password: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            exit(0)
            
        c.execute("SELECT hash FROM admins WHERE user=?", (u,))
        row = c.fetchone()
        
        if row != None:
            db_hash = row[0]
            entered_hash = hashlib.sha256(p.encode()).hexdigest()
            if entered_hash == db_hash:
                print("\nLogin successful! Welcome, %s." % u)
                return True
            else:
                print("Incorrect password!\n")
        else:
            print("User not found!\n")

def show(s):
    print("\n  Roll No    : " + str(s[0]))
    print("  Name       : " + s[1])
    print("  Branch     : " + s[2])
    print("  Semester   : " + str(s[3]))
    print("  Marks      : " + str(s[4]))
    print("  Phone      : " + s[5])
    print("  Email      : " + s[6])
    print()


def add_student():
    print("\n--- Add New Student ---")

    while True == True:
        r = input("Enter Roll Number: ").strip()
        if len(r)==0:
            print("Roll number can't be empty!")
            continue
        
        c.execute("SELECT * FROM studs WHERE r=?", (r,))
        dup = c.fetchone()
        
        if dup != None:
            print("This roll number already exists! Try a different one.")
            continue
        break

    while True == True:
        n = input("Enter Student Name: ").strip()
        if len(n) > 0:
            break
        print("Name can't be empty!")

    while True == True:
        b = input("Enter Branch (CSE, ECE, ME, etc): ").strip()
        if len(b)> 0:
            break
        print("Branch can't be empty!")

    while True == True:
        try:
            sm = int(input("Enter Semester (1-8): "))
            if sm < 1 or sm > 8:
                print("Semester should be between 1 and 8!")
                continue
            break
        except ValueError:
            print("Please enter a valid number!")

    while True == True:
        try:
            m = float(input("Enter Marks (out of 100): "))
            if m < 0 or m > 100:
                print("Marks should be between 0 and 100!")
                continue
            break
        except ValueError:
            print("Please enter a valid number!")

    # phone validation
    while True == True:
        p = input("Enter Phone Number: ").strip()
        if len(p)==0:
            print("Phone number can't be empty!")
            continue
        ok = True
        for x in p:
            if x.isdigit() == False and x != "+" and x != "-" and x != " ":
                ok = False
                break
        d = ""
        for x in p:
            if x.isdigit():
                d = d + x
        if ok == False or len(d) < 10:
            print("Enter a valid phone number (at least 10 digits)!")
            continue
        break

    e = input("Enter Email (press Enter to skip): ").strip()
    
    ee = "N/A"
    if len(e) > 0:
        ee = e

    c.execute("INSERT INTO studs VALUES (?, ?, ?, ?, ?, ?, ?)", (r, n, b.upper(), sm, m, p, ee))
    db.commit()
    print("\nStudent '%s' added successfully!\n" % n)


def view_all():
    print("\n--- All Student Records ---")

    c.execute("SELECT * FROM studs")
    rows = c.fetchall()

    if len(rows)==0:
        print("No students found! Add some first.\n")
        return

    print("\n%-12s %-20s %-8s %-5s %-8s %-15s %s" % ("Roll", "Name", "Branch", "Sem", "Marks", "Phone", "Email"))
    print("-" * 90)

    for s in rows:
        print("%-12s %-20s %-8s %-5s %-8s %-15s %s" % (s[0], s[1], s[2], str(s[3]), str(s[4]), s[5], s[6]))

    print("\nTotal: %d student(s)\n" % len(rows))


def find():
    print("\n--- Search Student ---")
    print("1. Search by Roll Number")
    print("2. Search by Name")

    try:
        ch = input("\nYour choice: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSearch cancelled.\n")
        return

    if ch == "1":
        r = input("Enter Roll Number: ").strip()
        c.execute("SELECT * FROM studs WHERE r=?", (r,))
        s = c.fetchone()
        
        if s != None:
            show(s)
        else:
            print("No student found with roll number '%s'\n" % r)
    else:
        if ch == "2":
            q = input("Enter Name (full or partial): ").strip().lower()
            if len(q)==0:
                print("Please enter something to search!\n")
                return
            
            c.execute("SELECT * FROM studs")
            rows = c.fetchall()
            
            res = []
            for s in rows:
                if q in s[1].lower():
                    res.append(s)
                    
            if len(res) > 0:
                print("\nFound %d result(s):" % len(res))
                for s in res:
                    show(s)
            else:
                print("No student found matching '%s'\n" % q)
        else:
            print("Invalid choice!\n")


def update():
    print("\n--- Update Student ---")

    r = input("Enter Roll Number of student to update: ").strip()

    c.execute("SELECT * FROM studs WHERE r=?", (r,))
    tgt = c.fetchone()

    if tgt == None:
        print("No student found with roll number '%s'\n" % r)
        return

    print("\nCurrent details:")
    show(tgt)

    print("What do you want to update?")
    print("1. Name")
    print("2. Branch")
    print("3. Semester")
    print("4. Marks")
    print("5. Phone")
    print("6. Email")
    print("7. Cancel")

    try:
        ch = input("\nYour choice: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nUpdate cancelled.\n")
        return

    if ch == "1":
        v = input("Enter new name: ").strip()
        if len(v) > 0:
            c.execute("UPDATE studs SET n=? WHERE r=?", (v, r))
            db.commit()
            print("Name updated!\n")
        else:
            print("Name can't be empty! Update cancelled.\n")
    else:
        if ch == "2":
            v = input("Enter new branch: ").strip()
            if len(v) > 0:
                c.execute("UPDATE studs SET b=? WHERE r=?", (v.upper(), r))
                db.commit()
                print("Branch updated!\n")
            else:
                print("Branch can't be empty! Update cancelled.\n")
        else:
            if ch == "3":
                try:
                    v = int(input("Enter new semester (1-8): "))
                    if v < 1 or v > 8:
                        print("Invalid semester! Update cancelled.\n")
                    else:
                        c.execute("UPDATE studs SET sm=? WHERE r=?", (v, r))
                        db.commit()
                        print("Semester updated!\n")
                except ValueError:
                    print("Invalid number! Update cancelled.\n")
            else:
                if ch == "4":
                    try:
                        v = float(input("Enter new marks (0-100): "))
                        if v < 0 or v > 100:
                            print("Marks should be between 0 and 100! Update cancelled.\n")
                        else:
                            c.execute("UPDATE studs SET m=? WHERE r=?", (v, r))
                            db.commit()
                            print("Marks updated!\n")
                    except ValueError:
                        print("Invalid number! Update cancelled.\n")
                else:
                    if ch == "5":
                        v = input("Enter new phone number: ").strip()
                        d = ""
                        for x in v:
                            if x.isdigit():
                                d = d + x
                        if len(d) >= 10:
                            c.execute("UPDATE studs SET p=? WHERE r=?", (v, r))
                            db.commit()
                            print("Phone updated!\n")
                        else:
                            print("Invalid phone number! Update cancelled.\n")
                    else:
                        if ch == "6":
                            v = input("Enter new email: ").strip()
                            ee = "N/A"
                            if len(v) > 0:
                                ee = v
                            c.execute("UPDATE studs SET e=? WHERE r=?", (ee, r))
                            db.commit()
                            print("Email updated!\n")
                        else:
                            if ch == "7":
                                print("Update cancelled.\n")
                            else:
                                print("Invalid choice!\n")


def delete_rec():
    print("\n--- Delete Student ---")

    r = input("Enter Roll Number of student to delete: ").strip()

    c.execute("SELECT n FROM studs WHERE r=?", (r,))
    s = c.fetchone()

    if s == None:
        print("No student found with roll number '%s'\n" % r)
        return

    nm = s[0]
    print("\nYou are about to delete: %s (Roll: %s)" % (nm, r))

    try:
        y = input("Are you sure? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nDeletion cancelled.\n")
        return

    if y == "y" or y == "yes":
        c.execute("DELETE FROM studs WHERE r=?", (r,))
        db.commit()
        print(nm + " has been deleted.\n")
    else:
        print("Deletion cancelled.\n")


# stats
def stats():
    print("\n--- Statistics ---")

    c.execute("SELECT * FROM studs")
    rows = c.fetchall()

    if len(rows)==0:
        print("No data available!\n")
        return

    t = len(rows)
    tm = 0
    h = rows[0][4]
    lo = rows[0][4]
    top = rows[0][1]

    for s in rows:
        tm = tm + s[4]
        if s[4] > h:
            h = s[4]
            top = s[1]
        if s[4] < lo:
            lo = s[4]

    a = round(tm / t, 2)

    bc = {}
    for s in rows:
        b = s[2]
        if b in bc:
            bc[b] = bc[b] + 1
        else:
            bc[b] = 1

    p = 0
    fx = 0
    for s in rows:
        if s[4] >= 40:
            p = p + 1
        else:
            fx = fx + 1

    print("  Total Students : %d" % t)
    print("  Average Marks  : %s" % str(a))
    print("  Highest Marks  : %s (%s)" % (str(h), top))
    print("  Lowest Marks   : %s" % str(lo))
    print("  Passed         : %d" % p)
    print("  Failed         : %d" % fx)
    print("\n  Branch-wise count:")
    for b in bc:
        print("    %s: %d" % (b, bc[b]))
    print()


def menu():
    print("=" * 42)
    print("   STUDENT DATA MANAGEMENT SYSTEM")
    print("=" * 42)
    print("   1. Add Student")
    print("   2. View All Students")
    print("   3. Search Student")
    print("   4. Update Student")
    print("   5. Delete Student")
    print("   6. View Statistics")
    print("   7. Exit")
    print("=" * 42)


def start():
    str_val = "init"
    res = ""
    for charx in str_val:
        if charx != " ":
            if charx != ".":
                if charx != ",":
                    if charx != "!":
                        if charx != "?":
                            if charx != "@":
                                if charx != "#":
                                    if charx != "$":
                                        if charx != "%":
                                            if charx != "^":
                                                if charx != "&":
                                                    if charx != "*":
                                                        if charx != "(":
                                                            if charx != ")":
                                                                if charx != "-":
                                                                    if charx != "_":
                                                                        if charx != "+":
                                                                            if charx != "=":
                                                                                res = res + charx

    login()

    while True == True:
        menu()

        try:
            ch = input("\nEnter your choice (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!\n")
            break

        if ch == "1":
            add_student()
        else:
            if ch == "2":
                view_all()
            else:
                if ch == "3":
                    find()
                else:
                    if ch == "4":
                        update()
                    else:
                        if ch == "5":
                            delete_rec()
                        else:
                            if ch == "6":
                                stats()
                            else:
                                if ch == "7":
                                    print("\nGoodbye!\n")
                                    break
                                else:
                                    print("\nInvalid choice! Please enter a number between 1 and 7.\n")

start()
