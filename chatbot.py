from pyswip import Prolog
import re

prolog = Prolog()
prolog.consult("family.pl")

def add_fact(statement):
    try:
        # handles mother father rs
        match = re.match(r"(father|mother|son|daughter|brother|sister|child|uncle|aunt)\((\w+),(\w+)\)", statement)
        if match:
            relation, a, b = match.groups()
            if a == b:
                raise ValueError("Self-reference detected.")

            # handles ancestry
            if relation in ["father", "mother", "son", "daughter", "child"]:
                if list(prolog.query(f"ancestor({b},{a})")):
                    raise ValueError("Circular ancestry detected.")

        # handles gender
        if statement.startswith("female("):
            name = re.match(r"female\((\w+)\)", statement).group(1)
            if list(prolog.query(f"male({name})")):
                raise ValueError("Gender contradiction: already male.")
        elif statement.startswith("male("):
            name = re.match(r"male\((\w+)\)", statement).group(1)
            if list(prolog.query(f"female({name})")):
                raise ValueError("Gender contradiction: already female.")

        prolog.assertz(statement)
        print("OK! I learned something.")
    except Exception:
        print("That’s impossible!")

def add_multiFact(statement):
    try:
        # handles mother father rs
        match = re.match(r"(father|mother|son|daughter|brother|sister|child|uncle|aunt)\((\w+),(\w+)\)", statement)
        if match:
            relation, a, b = match.groups()
            if a == b:
                raise ValueError("Self-reference detected.")

            # handles ancestry
            if relation in ["father", "mother", "son", "daughter", "child"]:
                if list(prolog.query(f"ancestor({b},{a})")):
                    raise ValueError("Circular ancestry detected.")

        # handles gender
        if statement.startswith("female("):
            name = re.match(r"female\((\w+)\)", statement).group(1)
            if list(prolog.query(f"male({name})")):
                raise ValueError("Gender contradiction: already male.")
        elif statement.startswith("male("):
            name = re.match(r"male\((\w+)\)", statement).group(1)
            if list(prolog.query(f"female({name})")):
                raise ValueError("Gender contradiction: already female.")

        prolog.assertz(statement)
    except Exception:
        print("That’s impossible!")

def ensure_gender_known(name: str, expected_gender: str):
    """Ask user for gender if not already known."""
    name = name.lower()
    known_male = list(prolog.query(f"male({name})"))
    known_female = list(prolog.query(f"female({name})"))

    if not known_male and not known_female:
        while True:
            user_input = input(f"{name.capitalize()}'s gender is unknown. Please enter gender (male/female): ").strip().lower()
            if user_input in {"male", "female"}:
                if user_input != expected_gender:
                    print(f"Warning: You indicated {name.capitalize()} is {user_input}, but the question implies {expected_gender}.")
                prolog.assertz(f"{user_input}({name})")
                break
            else:
                print("Invalid input. Please enter 'male' or 'female'.")
    
def handle_statement(prompt):
    prompt = prompt.strip('.')

    match = re.match(r"(\w+) is the father of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "male")
            add_fact(f"father({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is the mother of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "female")
            add_fact(f"mother({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return
    
    match = re.match(r"(\w+) and (\w+) are siblings", prompt)
    if match:
        try:
            add_multiFact(f"sibling({match.group(1).lower()},{match.group(2).lower()})")
            add_multiFact(f"sibling({match.group(2).lower()},{match.group(1).lower()})")
            print("OK! I learned something.")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is a (brother|sister) of (\w+)", prompt, re.IGNORECASE)
    if match:
        sibling1 = match.group(1).lower()
        relation = match.group(2).lower()
        sibling2 = match.group(3).lower()

        try:
            if relation == "brother":
                assert_gender(sibling1, "male")
                add_multiFact(f"brother({sibling1},{sibling2})")
            else:
                assert_gender(sibling1, "female")
                add_multiFact(f"sister({sibling1},{sibling2})")

            # Add symmetric sibling facts regardless of gender
            add_multiFact(f"sibling({sibling1},{sibling2})")
            add_multiFact(f"sibling({sibling2},{sibling1})")

            print("OK! I learned something.")
        except ValueError as ve:
            print(ve)
        return

    match = re.match(r"(\w+) and (\w+) are the parents of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "male")
            add_fact(f"father({match.group(1).lower()},{match.group(3).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        try:
            assert_gender(match.group(1).lower(), "female")
            add_fact(f"mother({match.group(2).lower()},{match.group(3).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is a child of (\w+)", prompt)
    if match:
        add_fact(f"child({match.group(1).lower()},{match.group(2).lower()})")
        return

    match = re.match(r"(\w+), (\w+) and (\w+) are children of (\w+)", prompt)
    if match:
        try:
            add_multiFact(f"child({match.group(1).lower()},{match.group(4).lower()})")
            add_multiFact(f"child({match.group(2).lower()},{match.group(4).lower()})")
            add_multiFact(f"child({match.group(3).lower()},{match.group(4).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is a (son|daughter) of (\w+)", prompt, re.IGNORECASE)
    if match:
        child = match.group(1).lower()
        relation = match.group(2).lower()
        parent = match.group(3).lower()

        try:
            if relation == "son":
                assert_gender(child, "male")
                add_multiFact(f"son({child},{parent})")
                add_multiFact(f"child({child},{parent})")
                add_multiFact(f"father({parent},{child})")
            elif relation == "daughter":
                assert_gender(child, "female")
                add_multiFact(f"daughter({child},{parent})")
                add_multiFact(f"child({child},{parent})")
                add_multiFact(f"mother({parent},{child})")
            print("OK! I learned something.")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is an uncle of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "male")
            add_fact(f"uncle({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is an aunt of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "female")
            add_fact(f"aunt({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    match = re.match(r"(\w+) is a grandmother of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "female")
            add_fact(f"grandmother({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return
    
    match = re.match(r"(\w+) is a grandfather of (\w+)", prompt)
    if match:
        try:
            assert_gender(match.group(1).lower(), "male")
            add_fact(f"grandfather({match.group(1).lower()},{match.group(2).lower()})")
        except ValueError as e:
            print("That’s impossible!")
            return
        return

    print("Sorry, I didn’t understand that statement.")

def handle_question(prompt):
    prompt = prompt.strip('?')

    match = re.match(r"Is (\w+) a daughter of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "female")
        result = list(prolog.query(f"daughter({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) a son of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "male")
        result = list(prolog.query(f"son({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) a sister of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "female")
        result = list(prolog.query(f"sister({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) a brother of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "male")
        result = list(prolog.query(f"brother({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) an aunt of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "female")
        result = list(prolog.query(f"aunt({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) an uncle of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "male")
        result = list(prolog.query(f"uncle({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) a grandmother of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "female")
        result = list(prolog.query(f"grandmother({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Is (\w+) a grandfather of (\w+)", prompt, re.IGNORECASE)
    if match:
        ensure_gender_known(match.group(1), "male")
        result = list(prolog.query(f"grandfather({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Are (\w+) and (\w+) siblings", prompt, re.IGNORECASE)
    if match:
        res1 = list(prolog.query(f"sibling({match.group(1).lower()},{match.group(2).lower()})"))
        res2 = list(prolog.query(f"sibling({match.group(2).lower()},{match.group(1).lower()})"))
        print("Yes!" if res1 or res2 else "No.")
        return

    match = re.match(r"Who are the siblings of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"sibling(X,{match.group(1).lower()})"))
        print("Siblings:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Who are the sisters of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"sister(X,{match.group(1).lower()})"))
        print("Sisters:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Who are the brothers of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"brother(X,{match.group(1).lower()})"))
        print("Brothers:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Is (\w+) the mother of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"mother({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Who is the mother of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"mother(X,{match.group(1).lower()})"))
        print("Mother:", result[0]["X"].capitalize() if result else "None found.")
        return

    match = re.match(r"Is (\w+) the father of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"father({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Who is the father of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"father(X,{match.group(1).lower()})"))
        print("Father:", result[0]["X"].capitalize() if result else "None found.")
        return

    match = re.match(r"Are (\w+) and (\w+) the parents of (\w+)", prompt, re.IGNORECASE)
    if match:
        f1 = list(prolog.query(f"father({match.group(1).lower()},{match.group(3).lower()})"))
        m1 = list(prolog.query(f"mother({match.group(2).lower()},{match.group(3).lower()})"))
        print("Yes!" if f1 and m1 else "No.")
        return

    match = re.match(r"Who are the parents of (\w+)", prompt, re.IGNORECASE)
    if match:
        child = match.group(1).lower()
        fathers = [r["X"].capitalize() for r in prolog.query(f"father(X,{child})")]
        mothers = [r["X"].capitalize() for r in prolog.query(f"mother(X,{child})")]
        parents = fathers + mothers
        print("Parents:", ", ".join(parents) if parents else "None found.")
        return

    match = re.match(r"Who are the daughters of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"daughter(X,{match.group(1).lower()})"))
        print("Daughters:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Who are the sons of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"son(X,{match.group(1).lower()})"))
        print("Sons:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Is (\w+) a child of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"child({match.group(1).lower()},{match.group(2).lower()})"))
        print("Yes!" if result else "No.")
        return

    match = re.match(r"Who are the children of (\w+)", prompt, re.IGNORECASE)
    if match:
        result = list(prolog.query(f"child(X,{match.group(1).lower()})"))
        print("Children:", ", ".join(sorted({r["X"].capitalize() for r in result})) if result else "None found.")
        return

    match = re.match(r"Are (\w+), (\w+) and (\w+) children of (\w+)", prompt, re.IGNORECASE)
    if match:
        c1, c2, c3, parent = match.groups()
        all_found = all(list(prolog.query(f"child({child.lower()},{parent.lower()})")) for child in (c1, c2, c3))
        print("Yes!" if all_found else "No.")
        return

    match = re.match(r"Are (\w+) and (\w+) relatives", prompt, re.IGNORECASE)
    if match:
        a, b = match.group(1).lower(), match.group(2).lower()
        result = list(prolog.query(f"related({a},{b})"))
        print("Yes!" if result else "No.")
        return

    print("Sorry, I didn’t understand that question.")

def assert_gender(name, gender):
    if gender == "male":
        if list(prolog.query(f"female({name})")):
            raise ValueError(f"Gender contradiction: {name.capitalize()} is already female.")
    elif gender == "female":
        if list(prolog.query(f"male({name})")):
            raise ValueError(f"Gender contradiction: {name.capitalize()} is already male.")
    prolog.assertz(f"{gender}({name})")

def main():
    print("Welcome to the Family Chatbot!")
    print("Enter a statement or question, or type 'exit' to quit.\n")

    while True:
        user_input = input("> ").strip()
        if user_input.lower() == 'exit':
            break
        elif user_input.endswith('?'):
            handle_question(user_input)
        elif user_input.endswith('.'):
            handle_statement(user_input)
        else:
            print("Please end your sentence with a period (.) or question mark (?)")

if __name__ == "__main__":
    main()