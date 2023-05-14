var row = 0
var target 
var targList


function startGame() {
    target = document.getElementById("target_text").value.trim()
    if (!(target.length == 5 && /^[a-z]+$/.test(target))) {
        document.getElementById("status").innerHTML = "invalid input"
    } else {
        document.getElementById("status").innerHTML = "Start"
        targList = target.split('')
    }  
}

function makeGuess() {
    let guessWord = document.getElementById("guess_text").value.trim();
    if (!(guessWord.length == 5 && /^[a-z]+$/.test(guessWord))) {
        document.getElementById("status").innerHTML = "invalid input"
    }
    else {
        document.getElementById("status").innerHTML = "valid input"
        for (let col = 0; col < 5; col++) {
            let currCell = document.getElementById("cell_" + row + "_" + col)
            currCell.innerHTML = guessWord[col]

            //checking greens first
            if (target[col] == guessWord[col]) {
                currCell.style.backgroundColor = "rgb(124,252,0)"
                index = targList.indexOf(target[col])
                targList.splice(index, 1)

                //entire word is correct
                if (target == guessWord) {
                    document.getElementById("status").innerHTML = "You win!"
                }
            }
        }
        
        //checking the rest of the cells
        for (let col = 0; col < 5; col++) {
            let currCell = document.getElementById("cell_" + row + "_" + col)
            if (target[col] == guessWord[col]) {
                continue
            } else if (targList.includes(guessWord[col])) {
                currCell.style.backgroundColor = "rgb(255,255,51)"
                index = targList.indexOf(guessWord[col])
                targList.splice(index, 1)

            } else {
                currCell.style.backgroundColor = "gray"
            }
        }

        targList = target.split('')
        row += 1 
        if (row == 6) {
            document.getElementById("status").innerHTML = "You lose!"
        }
    }
}
