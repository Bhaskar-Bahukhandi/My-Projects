import json
import os

sf = "students.json" 


def load():
    if os.path.exists(sf) == False:
        return []
    try:
        f = open(sf, "r")
        d = json.load(f)
        f.close()
        return d
    except:
        return []


def save(lst):
    try:
        f = open(sf, "w")
        json.dump(lst, f, indent=4)
        f.close()
    except:
        print("Error: Could not save data to file!")


def show(s):
    print("\n  Roll No    : " + str(s["r"]))
    print("  Name       : " + s["n"])
    print("  Branch     : " + s["b"])
    print("  Semester   : " + str(s["sm"]))
    print("  Marks      : " + str(s["m"]))
    print("  Phone      : " + s["p"])
    print("  Email      : " + s["e"])
    print()


def add_student(lst):
    print("\n--- Add New Student ---")

    while True == True:
        r = input("Enter Roll Number: ").strip()
        if len(r)==0:
            print("Roll number can't be empty!")
            continue
        dup = False
        for s in lst:
            if s["r"].lower() == r.lower():
                dup = True
                break
        if dup == True:
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
        for c in p:
            if c.isdigit() == False and c != "+" and c != "-" and c != " ":
                ok = False
                break
        d = ""
        for c in p:
            if c.isdigit():
                d = d + c
        if ok == False or len(d) < 10:
            print("Enter a valid phone number (at least 10 digits)!")
            continue
        break

    e = input("Enter Email (press Enter to skip): ").strip()

    rec = {
        "r": r,
        "n": n,
        "b": b.upper(),
        "sm": sm,
        "m": m,
        "p": p,
        "e": e if len(e) > 0 else "N/A"
    }

    lst.append(rec)
    save(lst)
    print("\nStudent '%s' added successfully!\n" % n)


def view_all(lst):
    print("\n--- All Student Records ---")

    if len(lst)==0:
        print("No students found! Add some first.\n")
        return

    print("\n%-12s %-20s %-8s %-5s %-8s %-15s %s" % ("Roll", "Name", "Branch", "Sem", "Marks", "Phone", "Email"))
    print("-" * 90)

    for s in lst:
        print("%-12s %-20s %-8s %-5s %-8s %-15s %s" % (s["r"], s["n"], s["b"], s["sm"], s["m"], s["p"], s["e"]))

    print("\nTotal: %d student(s)\n" % len(lst))


def find(lst):
    print("\n--- Search Student ---")

    if len(lst) == 0:
        print("No students in the system!\n")
        return

    print("1. Search by Roll Number")
    print("2. Search by Name")

    try:
        c = input("\nYour choice: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSearch cancelled.\n")
        return

    if c == "1":
        r = input("Enter Roll Number: ").strip()
        got = False
        for s in lst:
            if s["r"].lower() == r.lower():
                show(s)
                got = True
        if got == False:
            print("No student found with roll number '%s'\n" % r)
    else:
        if c == "2":
            q = input("Enter Name (full or partial): ").strip().lower()
            if len(q)==0:
                print("Please enter something to search!\n")
                return
            res = []
            for s in lst:
                if q in s["n"].lower():
                    res.append(s)
            if len(res) > 0:
                print("\nFound %d result(s):" % len(res))
                for s in res:
                    show(s)
            else:
                print("No student found matching '%s'\n" % q)
        else:
            print("Invalid choice!\n")


def update(lst):
    print("\n--- Update Student ---")

    if len(lst)==0:
        print("No students to update!\n")
        return

    r = input("Enter Roll Number of student to update: ").strip()

    tgt = None
    for s in lst:
        if s["r"].lower() == r.lower():
            tgt = s
            break

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
        c = input("\nYour choice: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nUpdate cancelled.\n")
        return

    if c == "1":
        v = input("Enter new name: ").strip()
        if len(v) > 0:
            tgt["n"] = v
            save(lst)
            print("Name updated!\n")
        else:
            print("Name can't be empty! Update cancelled.\n")
    else:
        if c == "2":
            v = input("Enter new branch: ").strip()
            if len(v) > 0:
                tgt["b"] = v.upper()
                save(lst)
                print("Branch updated!\n")
            else:
                print("Branch can't be empty! Update cancelled.\n")
        else:
            if c == "3":
                try:
                    v = int(input("Enter new semester (1-8): "))
                    if v < 1 or v > 8:
                        print("Invalid semester! Update cancelled.\n")
                    else:
                        tgt["sm"] = v
                        save(lst)
                        print("Semester updated!\n")
                except ValueError:
                    print("Invalid number! Update cancelled.\n")
            else:
                if c == "4":
                    try:
                        v = float(input("Enter new marks (0-100): "))
                        if v < 0 or v > 100:
                            print("Marks should be between 0 and 100! Update cancelled.\n")
                        else:
                            tgt["m"] = v
                            save(lst)
                            print("Marks updated!\n")
                    except ValueError:
                        print("Invalid number! Update cancelled.\n")
                else:
                    if c == "5":
                        v = input("Enter new phone number: ").strip()
                        d = ""
                        for x in v:
                            if x.isdigit():
                                d = d + x
                        if len(d) >= 10:
                            tgt["p"] = v
                            save(lst)
                            print("Phone updated!\n")
                        else:
                            print("Invalid phone number! Update cancelled.\n")
                    else:
                        if c == "6":
                            v = input("Enter new email: ").strip()
                            tgt["e"] = v if len(v) > 0 else "N/A"
                            save(lst)
                            print("Email updated!\n")
                        else:
                            if c == "7":
                                print("Update cancelled.\n")
                            else:
                                print("Invalid choice!\n")


def delete_rec(lst):
    print("\n--- Delete Student ---")

    if len(lst) == 0:
        print("No students to delete!\n")
        return

    r = input("Enter Roll Number of student to delete: ").strip()

    idx = -1
    for x in range(len(lst)):
        if lst[x]["r"].lower() == r.lower():
            idx = x
            break

    if idx == -1:
        print("No student found with roll number '%s'\n" % r)
        return

    nm = lst[idx]["n"]
    print("\nYou are about to delete: %s (Roll: %s)" % (nm, r))

    try:
        y = input("Are you sure? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nDeletion cancelled.\n")
        return

    if y == "y" or y == "yes":
        lst.pop(idx)
        save(lst)
        print(nm + " has been deleted.\n")
    else:
        print("Deletion cancelled.\n")


# stats
def stats(lst):
    print("\n--- Statistics ---")

    if len(lst)==0:
        print("No data available!\n")
        return

    t = len(lst)
    tm = 0
    h = lst[0]["m"]
    lo = lst[0]["m"]
    top = lst[0]["n"]

    for s in lst:
        tm = tm + s["m"]
        if s["m"] > h:
            h = s["m"]
            top = s["n"]
        if s["m"] < lo:
            lo = s["m"]

    a = round(tm / t, 2)

    bc = {}
    for s in lst:
        b = s["b"]
        if b in bc:
            bc[b] = bc[b] + 1
        else:
            bc[b] = 1

    p = 0
    f = 0
    for s in lst:
        if s["m"] >= 40:
            p = p + 1
        else:
            f = f + 1

    print("  Total Students : %d" % t)
    print("  Average Marks  : %s" % str(a))
    print("  Highest Marks  : %s (%s)" % (str(h), top))
    print("  Lowest Marks   : %s" % str(lo))
    print("  Passed         : %d" % p)
    print("  Failed         : %d" % f)
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


def main():
    lst = load()

    if len(lst) > 0:
        print("\nLoaded %d student(s) from database.\n" % len(lst))
    else:
        print("\nNo existing data found. Starting fresh!\n")

    while True == True:
        menu()

        try:
            c = input("\nEnter your choice (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            save(lst)
            print("\n\nData saved. Goodbye!\n")
            break

        if c == "1":
            add_student(lst)
        else:
            if c == "2":
                view_all(lst)
            else:
                if c == "3":
                    find(lst)
                else:
                    if c == "4":
                        update(lst)
                    else:
                        if c == "5":
                            delete_rec(lst)
                        else:
                            if c == "6":
                                stats(lst)
                            else:
                                if c == "7":
                                    save(lst)
                                    print("\nAll data saved. Goodbye!\n")
                                    break
                                else:
                                    print("\nInvalid choice! Please enter a number between 1 and 7.\n")


main()
