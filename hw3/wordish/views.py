from django.shortcuts import render
import traceback

# Create your views here.
def start_action(request):
    if request.method == "GET":
        context = {"message": "Welcome to Wordish"}
        return render(request, "wordish/start-page.html", context)

    try:
        #put in target word
        target = process_word_parameter(request.POST, "target")
        context = compute_context(target, guesses=[])
        return render(request, "wordish/game-page.html", context)

    except Exception as e:
        print(traceback.format_exc()) 
        context = {"message": str(e)}
        return render(request, "wordish/start-page.html", context)

def guess_action(request):
    if request.method == "GET":
        context = {"message": "You're hacking.  Try again!"}
        return render(request, "wordish/start-page.html", context)

    try:
        target = process_word_parameter(request.POST, "target")
        old_guesses = process_old_guesses(request.POST)

    except Exception as e:
        return render(request, "wordish/start-page.html", {"message": f"Fatal error: {e}"})
    
    try:    
        new_guess = process_word_parameter(request.POST, "new-guess")
        context = compute_context(target, old_guesses + [new_guess])
        
    except Exception as e:
        context = compute_context(target, old_guesses)
        context["status"] = f"Invalid input: {e}"
        # if ("invalid input" in str(e)):
        #     return render(request, "wordish/game-page.html", context)
        # else:
        #     return render(request, "wordish/start-page.html", context)
    return render(request, "wordish/game-page.html", context)
    

def compute_context(target, guesses):
    matrix = [[col for col in range(5)] for row in range(6)]
    status = "Start play"
    targList = list(target)

    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            matrix[row][col] = {"id": "cell_" + str(row) + "_" + str(col)}
   
    for row in range(len(guesses)):
        for col in range(0, 5):
            matrix[row][col]["letter"] = guesses[row][col]
            status = "valid guess"
            
            #check greens first
            if (target[col] == guesses[row][col]):
                matrix[row][col]["color"] = "green"
                targList.remove(target[col])

                #entire word is correct
                if (target == guesses[row]):
                    status = "You win!"
        
        #check yellows and grays
        for col in range(0, 5):
            if (target[col] == guesses[row][col]):
                continue
            elif (guesses[row][col] in targList):
                matrix[row][col]["color"] = "yellow"
                targList.remove(guesses[row][col])
            else:
                matrix[row][col]["color"] = "gray"
            
        targList = list(target)
        if (row == 5):
            status = "You lose!"
        
    context = {
        "status": status,
        "matrix": matrix,
        "target": target,
        "old_guesses": ' '.join(guesses),
    }
    return context


def process_old_guesses(request):
    guesses = []
    old_guesses = request["old-guesses"].split()

    for guess in old_guesses:
        guesses.append(process_word(guess))
    return guesses
    
def process_word(word):
    if len(word) != 5 or not word.isalpha():
        raise ValueError("Hidden Field Invalid")
    else:
        return word

def process_word_parameter(request, target):
    word = request[target]
    if len(word) != 5 or not word.isalpha():
        raise ValueError("invalid input")
    else:
        return word
