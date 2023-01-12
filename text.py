def disemvowel(string_: str) -> str:
    vowels = ["a", "e", "i", "o", "u"]
    string_results = [
        letter for letter in string_ if letter.lower() not in vowels]
    string_results = "".join(string_results)

    return string_results


print(disemvowel("This website is for losers LOL!"))
