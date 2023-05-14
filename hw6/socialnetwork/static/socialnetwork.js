"use strict"

// Sends a new request to update the to-do list

// function loadG() {
//     loadPosts('global')
// }

function loadPosts(stream) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    if (stream == 'follower') {
        xhr.open("GET", "/socialnetwork/get-follower", true)
    } else if (stream == 'global') {
        xhr.open("GET", "/socialnetwork/get-global", true)
    }
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        //console.log(response)
        updateList(response)
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

function updateList(items) {
    // Removes all existing to-do list items
    let list = document.getElementById("my-posts-go-here")
    // while (list.hasChildNodes()) {
    //     list.firstChild.remove()
    // }
    // Adds each to do list item received from the server to the displayed list
    items['Posts'].forEach(item => {
            if (document.getElementById("id_post_div_" + item.id) === null) {
                list.prepend(makePostItemElement(item))
            }
        }
    )
    updateComments(items)
}

function updateComments(items) {
    let list = document.getElementById("my-posts-go-here")
    let allComments = items['Comments']
    var children = list.children;
    for (var i = 0; i < children.length; i++) {
        var pElem = children[i];
        allComments.forEach(comment => {
            if (comment.post_id== pElem.id.slice(-1)) {
                let commentDiv = document.getElementById("my-comments-go-here-for-post-" + pElem.id.slice(-1))
                let commentChild = document.getElementById("id_comment_div_" + comment.id)
                if (commentChild === null) {
                    commentDiv.prepend(makeCommentItemElement(comment))
                }
            }
        })
    }
}

// Builds a new HTML "li" element for the to do list
//item is a dictionary for specific comment
function makeCommentItemElement(item) {
    let element = document.createElement("div")
    element.id = "id_comment_div_" + item.id
    element.classList.add("comment_div")
    let name = item['first_name'] + " " +item['last_name']
    let profile = "<a " + "class=profile id=id_comment_profile_" + item.id + " href='../otherprofile/" + item['user_id'] + "/" + " '> " + name +" </a> " 
    let commenttext = "<label class=texts id=id_comment_text_" + item.id + ">" + sanitize(item['text']) + "</label>"
    let dt = new Date(item['creation_time'])
    let fixeddt = sanitize(dt.toLocaleDateString()) + ' ' + sanitize(dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))
    let datetime = "<label class=date id=id_comment_date_time_" + item.id + ">" + fixeddt + "</label>"
    element.innerHTML = `Comment by ${profile} - ${commenttext} - ${datetime}`
    return element
} 

 
// Builds a new HTML "li" element for the to do list
function makePostItemElement(item) {

    let element = document.createElement("div")
    element.id = "id_post_div_" + item.id
    let name = item['first_name'] + " " +item['last_name']
    let profile = "<a " + "class=profile id=id_post_profile_" + item.id + " href='../otherprofile/" + item['user_id'] + "/" + " '> " + name +" </a> " 
    let posttext = "<label class=texts id=id_post_text_" + item.id + ">" + sanitize(item['text']) + "</label>"
    let dt = new Date(item['creation_time'])
    let fixeddt = sanitize(dt.toLocaleDateString()) + ' ' + sanitize(dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))
    let datetime = "<label class=date id=id_post_date_time_" + item.id + ">" + fixeddt + "</label>"
    element.innerHTML = `Post by ${profile} - ${posttext} - ${datetime}`
    let newComment = document.createElement("div")
    newComment.id = "my-comments-go-here-for-post-" + item.id
    newComment.innerHTML = `<label>New Comment:</label> <input id="id_comment_input_text_${item.id}" type="text" name="comment_text"><button onclick="addComment(${item.id})" id="id_comment_button_${item.id}">Submit</button>`
    element.appendChild(newComment) 
    
    return element
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addItem() {
    let itemTextElement = document.getElementById("id_post_input_text")
    let itemTextValue = itemTextElement.value

    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("POST", addItemURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`item=${itemTextValue}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function addComment(post_id) {
    let itemTextElement = document.getElementById("id_comment_input_text_" + String(post_id))
    let itemTextValue = itemTextElement.value
    //console.log(itemTextElement.value)
    // Clear input box and old error message (if any)
    // itemTextElement.value = ''
    // displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("POST", addCommentURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`comment_text=${itemTextValue}&csrfmiddlewaretoken=${getCSRFToken()}&post_id=${post_id}`)
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