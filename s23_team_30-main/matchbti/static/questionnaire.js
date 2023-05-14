let map;
var x = document.getElementById("result");

function getLocation() {
    if (navigator.geolocation) {
        x.innerHTML = "Loading...";
        navigator.geolocation.getCurrentPosition(success, error);
    } else { 
        x.innerHTML = "Geolocation is not supported by this browser";
    }
}

function success(position) {
    x.innerHTML = "Success!";
    $.ajax({
        url: '/geolocation', 
        type: 'POST',
        data: `latitude=${position.coords.latitude}&longitude=${position.coords.longitude}&csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType : "json",
        success: window.location.href = '/'
    });
}

function error(err) {
    x.innerHTML = "Please enable your location to proceed";
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}