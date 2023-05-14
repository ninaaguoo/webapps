//"use strict"
let next = false;
// Sends a new request to update the to-do list

// function loadG() {
//     loadPosts('global')
// }

function loadProfiles() {
    // console.log("laoding")
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateGlobalPage(xhr)
    }
    xhr.open("GET", "/matchbti/get-global", true)
    xhr.send()
}

function loadMatches() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateMatchesPage(xhr)
    }
    xhr.open("GET", "/matchbti/get-matches", true)
    xhr.send()
}

function loadMessages(receiver_id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateMessagesPage(xhr)
    }
    console.log(receiver_id)
    xhr.open("GET", "/matchbti/get-messages/" + String(receiver_id), true)
    xhr.send()
}

function updateMessagesPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateMessages(response)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function updateMatchesPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateMatches(response)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function updateGlobalPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        //needs more than 1 user registered to show discovery feed
        updateList(response)
        //console.log("update page")
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function updateMessages(items) {
    console.log("!!!!!!update the messages", items)
    
    // let user_messages = document.getElementById("my-user-messages-go-here")
    // let receiver_messages = document.getElementById("my-receiver-messages-go-here")
    let messages = document.getElementById("my-messages-go-here")
    items.forEach(item => {
        console.log("for", item.id, item.text, document.getElementById("id_message_div_" + item.id) === null )
            if (document.getElementById("id_message_div_" + item.id) === null) {
                console.log(item)
                messages.append(makeMessageItemElement(item))
            }
        }
    )
    
    // items['user_messages'].forEach(item => {
    //         console.log(item.id)
    //         if (document.getElementById("id_user_message_div_" + item.id) === null) {
    //             user_messages.append(makeMessageItemElement(item))
    //         }
    //     }
    // )
    // items['receiver_messages'].forEach(item => {
    //         if (document.getElementById("id_receiver_message_div_" + item.id) === null) {
    //             receiver_messages.append(makeMessageItemElement(item))
    //         }
    //     }
    // )
}

function updateMatches(items) {
    //console.log("update the fucking matches")
    //console.log(items)
    let matches = document.getElementById("my-matches-go-here")
    matches.innerHTML = ""
    if (items.length > 0) {
        items.forEach(item => {
            matches.append(makeMatchItemElement(item))}
        )
    }
    else {
        let element = document.createElement("div")
        element.className = "center"
        element.innerHTML = "No matches yet"
        matches.append(element)
    }
}

//items: list of all compatible profiles
//should show one profile at a time use like and unlike to update to next profile
function updateList(items) {
    let curr_profile = document.getElementById("my-profiles-go-here")
    curr_profile.innerHTML = ""
    // console.log(items[0])
    if (items.length > 0) {
        curr_profile.append(makeProfileItemElement(items[0]))
    }
    else {
        let element = document.createElement("div")
        element.className = "center"
        element.innerHTML = "No more profiles"
        curr_profile.append(element)
    }
    // console.log("end of update")
}

function makeProfileItemElement(item) {
    let element = document.createElement("div")
    element.className = "card"
    element.id = "id_profile_div_" + item.id
    let name = item.first_name + " " +item.last_name
    element.innerHTML = `<div class="center"> <img id="id_user_picture" src="photo/${item.id}"> </div>
                        <div class="profileTitle"> ${name} </div <br>
                        <div class="profileInfo">
                            <table>
                                <tr>
                                    <td style="width:33%"> ${item.sexuality} ${item.gender} </td>
                                    <td style="width:33%"> ${item.age} </td>
                                    <td> ${item.height}ft ${item.heightInches}in </td>
                                </tr>
                                    <td> ${item.ethnicity} </td>
                                    <td> ${item.religion} </td>
                                    <td> ${item.mbti} </td>
                                </tr>
                            </table>
                            <br>
                            <table>
                                <tr>
                                    <td class="rowLabel"> Bio </td>
                                    <td class="info"> ${item.bio} </td>
                                </tr>
                                <tr>
                                    <td class="rowLabel"> School </td>
                                    <td class="info"> ${item.school} </td>
                                </tr>
                                <tr>
                                    <td class="rowLabel"> Work </td>
                                    <td> ${item.work} </td>
                                </tr>
                            </table>
                        </div>`
    let likeDislike = document.createElement("div")
    likeDislike.className = "center"
    likeDislike.innerHTML = `<button class="swipeButton" onclick="Dislike(${item.id})" id="id_dislike_button_${item.id}"> <i class="fa fa-close"></i> </button>
                             <button class="swipeButton" onclick="Like(${item.id})" id="id_like_button_${item.id}"> <i class="fa fa-heart"></i> </button>`
    element.appendChild(likeDislike) 
    return element
}

function makeMessageItemElement(item) {
    console.log("makeMessageItemElement", item.id, item.text)

    let element = document.createElement("div")
    element.id = "id_message_div_" + item.id
    if (item.curr_user == true)  {
        element.className = "user_messages"
    } else {
        element.className = "receiver_messages"
    }
    let name = item['first_name'] + " " +item['last_name']
    let text = "<label class=texts id=id_message_text_" + item.id + ">" + sanitize(item['text']) + "</label>"
    let dt = new Date(item['creation_time'])
    let fixeddt = sanitize(dt.toLocaleDateString()) + ' ' + sanitize(dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))
    let datetime = "<label class=date id=id_message_date_time_" + item.id + ">" + fixeddt + "</label>"
    element.innerHTML = `${text}`
    return element
}

function makeMatchItemElement(item) {
    let element = document.createElement("div")
    element.id = "id_profile_div_" + item.id
    element.className = "match"
    let name = item.first_name + " " +item.last_name
    element.innerHTML = `<img class="matchPic" id="id_user_picture" src="../photo/${item.id}"> ${name}
                         <div class="matchButtons">
                            <button class="matchButton" onclick="Chat(${item.id})" id="id_chat_button_${item.id}"> <i class='far fa-comments'></i> Chat </button>
                            <button class="matchButton" onclick="Unmatch(${item.id})" id="id_unmatch_button_${item.id}"> <i class="fa-solid fa-heart-crack"></i> Unmatch </button>
                         </div>`
    return element
} 

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function Chat(id) {
    // console.log(id)
    // console.log( window.location.origin )
    window.location.href =  window.location.origin +  "\\chat/"  + String(id)
    // console.log(id)
    loadMessages(id)
}

function Unmatch(user_id) {
    let itemTextElement = document.getElementById("id_unmatch_button_" + String(user_id))

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateMatches(xhr)
    }

    xhr.open("POST", unmatchURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}&id=${user_id}`)
    // console.log("finished unmatch")
}

function Like(user_id) {
    next = true
    let itemTextElement = document.getElementById("id_like_button_" + String(user_id))

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateGlobalPage(xhr)
    }

    xhr.open("POST", likeURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}&id=${user_id}`)
    // console.log("finished liking")
}

function Dislike(user_id) {
    next = true
    let itemTextElement = document.getElementById("id_dislike_button_" + String(user_id))

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateGlobalPage(xhr)
    }

    xhr.open("POST", dislikeURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}&id=${user_id}`)
}

function addMessage(user_id, receiver_id) {
    let itemTextElement = document.getElementById("id_message_input_text")
    let itemTextValue = itemTextElement.value

    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateMessagesPage(xhr)
    }

    xhr.open("POST", addMessageURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    console.log("adding a message")
    console.log(itemTextValue)
    xhr.send(`item=${itemTextValue}&csrfmiddlewaretoken=${getCSRFToken()}&user_id=${user_id}&receiver_id=${receiver_id}`)
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}
