"use strict"

// direct button to functions
document.addEventListener("DOMContentLoaded", function () {
    console.log('DOM fully loaded and parsed')
    // Add listeners to all buttons, prevent error if element is not visible
    try {
        document.querySelector("#username").addEventListener("click", () =>
            show_profile(document.querySelector("#username").innerHTML))
    } catch (err) { }

    try {
        document.querySelector("#following").addEventListener("click", () =>
            show_all_posts(1, document.querySelector("#username").innerHTML, 1))
    } catch (err) { }

    try {
        document.querySelector("#new_post").addEventListener("click", () =>
            new_post())
    } catch (err) { }
    // By default, load all posts
    show_all_posts(1)
})

// change sub heading on page
function change_heading(text) {
    var div = document.createElement("div")
    div.innerHTML = text
    document.querySelector("#heading-view").innerHTML = ""
    document.querySelector("#heading-view").appendChild(div)
}

// show all posts, or all posts from one user
function show_all_posts(page_num, username = "", following = "") {

    if (username === "") {
        change_heading("All Posts")
        try { document.querySelector("#profile-view").style.display = "none" } catch (err) { }
        try { document.querySelector("#new-post-view").style.display = "block" } catch (err) { }
    }

    if (following === 1) {
        change_heading("Following")
        try { document.querySelector("#profile-view").style.display = "none" } catch (err) { }
        try { document.querySelector("#new-post-view").style.display = "none" } catch (err) { }
        username = document.querySelector("#login_user").value
    }

    fetch("/all_posts/" + page_num + "/" + username + "/" + following, { method: "GET" })
        .then(response => response.json())
        .then(results => {

            var page_num = results[0]
            var num_pages = results[1]
            var posts = results[2]
            var prev = ""
            var next = ""

            if (page_num != 1) {
                //add previous page button
                var prev = document.createElement("button")
                prev.className = "btn btn-sm btn-outline-primary"
                prev.innerHTML = "Previous"
                prev.addEventListener("click", () => show_all_posts(page_num - 1, username, following))
            }

            if (page_num < num_pages) {
                //add next page button
                var next = document.createElement("button")
                next.className = "btn btn-sm btn-outline-primary"
                next.innerHTML = "Next"
                next.addEventListener("click", () => show_all_posts(page_num + 1, username, following))
            }

            list_posts(posts, prev, next)
        })
}

// helper to display posts
function list_posts(posts, prev, next) {

    // clear contents
    document.querySelector("#all-posts-view").innerHTML = ""

    // list posts
    posts.forEach(p => {
        //p[0] id, 1 username, 2 body, 3 timestamp
        // add container
        var view = document.createElement("div")
        view.className = "single-post-view"
        document.querySelector("#all-posts-view").appendChild(view)

        // add username
        var user = document.createElement("div")
        user.innerHTML = p[1].bold()
        if (document.querySelector("#username")) {  // allow profile page view only if logged in
            user.addEventListener("click", function () {
                show_profile(p[1])  //go to profile
            })
        }
        view.appendChild(user)

        // add post content
        var body = document.createElement("div")
        body.innerHTML = p[2]
        view.appendChild(body)
        var likes_time = document.createElement("div")
        view.appendChild(likes_time)

        // if logged in , add like button , add like stats
        if (document.querySelector("#username")) {
            var login_user = document.querySelector("#username").innerHTML
            var like_button = document.createElement("button")
            like_button.className = "btn btn-sm btn-outline-primary"
            like_button.innerHTML = "Like"
            like_button.addEventListener("click", function () {
                // make api call
                fetch("/like", {
                    method: "POST",
                    body: JSON.stringify({
                        post_id: p[0],
                        toggle: 1
                    })
                }).then(response => response.json())
                    .then(results => {
                        //update buttons and stats without re-POST
                        var num_like = likes_time.innerHTML.replace('<b>', "").split(" ")[0]
                        if (results[0] === "like created") {
                            num_like++
                            like_button.innerHTML = "Unlike"
                        } else if (results[0] === "like deleted") {
                            num_like--
                            like_button.innerHTML = "Like"
                        }
                        var ts = likes_time.innerHTML.split(" ")[2]
                        likes_time.innerHTML = "<b>" + num_like + " Likes</b> " + ts
                    })
            })
            view.appendChild(like_button)

            //if poster is user, also add edit button
            if (document.querySelector("#username").innerHTML === p[1]) {
                var edit = document.createElement("button")
                edit.className = "btn btn-sm btn-outline-primary"
                edit.innerHTML = "Edit"
                edit.addEventListener("click", function () {
                    //edit post
                })
                view.appendChild(edit)
            }

            //update like stats
            fetch("/like", {
                method: "POST",
                body: JSON.stringify({
                    post_id: p[0],
                    toggle: 0
                })
            }).then(response => response.json())
                .then(result => {
                    if (result[1]) { //if user already liked make unlike button
                        like_button.innerHTML = "Unlike"
                    }
                    //how many times post is liked
                    likes_time.innerHTML = "<b>" + result[0] + " Likes</b> " + p[3].toString()
                })
        }
    })

    //add button, if a button was made
    try { document.querySelector("#all-posts-view").appendChild(prev) } catch (err) { }
    try { document.querySelector("#all-posts-view").appendChild(next) } catch (err) { }
}

// create new post
function new_post() {
    // check for empty string
    const body = document.querySelector("#new-post-textarea").value.toString()
    if (!/\S/.test(body)) {
        document.querySelector("#new-post-callback").innerHTML = ("Post cannot be empty!").italics()
        return
    }
    // make api call
    fetch("/new_post", {
        method: "POST",
        body: JSON.stringify({
            body: document.querySelector("#new-post-textarea").value
        })
    })
        .then(response => response.json())
        .then(result => {
            // display post status message or error
            var element = document.createElement("div")
            element.id = "post-status"
            if (result.message === undefined) {
                element.innerHTML = result.error.italics()
            } else if (result.error === undefined) {
                element.innerHTML = result.message.italics()
            } else {
                element.innerHTML = ("Unknown Error").italics()
            }
            // add to page and animate
            document.querySelector("#new-post-callback").innerHTML = ""
            document.querySelector("#new-post-callback").appendChild(element)
            element.style.animationPlayState = 'running'
            document.querySelector("#new-post-textarea").value = ""
            show_all_posts(1)
        })
}

// show profile page
function show_profile(profile_user) {
    change_heading(profile_user)
    document.querySelector("#profile-view").style.display = "block"
    document.querySelector("#new-post-view").style.display = "none"
    show_all_posts(1, profile_user)

    //clear follow button, check if it should be added back later
    document.querySelector("#follow-button").innerHTML = ""

    // get follow info
    const login_user = document.querySelector("#login_user").value
    fetch("/follow", {
        method: "POST",
        body: JSON.stringify({ followee: profile_user, toggle: 0 }),
        headers: { 'Content-type': 'application/json; charset=UTF-8' }
    })
        .then(response => response.json())
        .then(result => {

            //show number of followers / following
            document.querySelector("#followers-view").innerHTML = result[1] + " Followers"
            document.querySelector("#following-view").innerHTML = result[2] + " Following"

            // make follow button if not same person
            if (login_user != profile_user) {
                var button = document.createElement("button")
                button.className = "btn btn-sm btn-outline-primary"
                button.id = "toggle-follow"
                if (result[0] === "pair exists") {
                    document.querySelector("#heading-view").innerHTML = profile_user +
                        "&nbsp;&nbsp;&nbsp;&nbsp;<span id='follow-span'><i>following</i></span>"
                    button.innerHTML = "Unfollow"
                } else {
                    button.innerHTML = "Follow"
                }
                // attach button and button action
                document.querySelector("#follow-button").appendChild(button)
                button.addEventListener("click", () => {
                    fetch("/follow", {
                        method: "POST",
                        body: JSON.stringify({ followee: profile_user, toggle: "1" })
                    }).then(response => response.json())
                        .then(result => { show_profile(profile_user) })
                })
            }
        })
}