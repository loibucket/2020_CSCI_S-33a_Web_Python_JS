"use strict"

// direct button to functions
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed")

    //all posts
    try { document.querySelector("#all-posts").addEventListener("click", () => sessionStorage.clear()) } catch (err) { }

    //logout
    try {
        document.querySelector("#logout").addEventListener("click", () => {
            sessionStorage.clear()
            show_all_posts(1)
            console.log('logout')
        })
    } catch (err) { /*button not found*/ }
    try { document.querySelector("#new-post").addEventListener("click", () => new_post()) } catch (err) { }

    //username
    try {
        document.querySelector("#username").addEventListener("click", () => {
            let user = document.querySelector("#username").innerHTML
            show_profile(user)
            show_all_posts(1, user)
        })
    } catch (err) { /*button not found*/ }

    //following
    try {
        document.querySelector("#following").addEventListener("click", () => show_all_posts(1, "", 1))
    } catch (err) { /*button not found*/ }

    //get last recorded state
    var g_page_num = sessionStorage.getItem('g_page_num') || 1
    var g_username = sessionStorage.getItem('g_username') || ""
    var g_following = sessionStorage.getItem('g_following') || ""
    show_all_posts(g_page_num, g_username, g_following)
})

// change sub heading on page
function change_heading(text) {
    var div = document.createElement("div")
    div.innerHTML = text
    document.querySelector("#heading-view").innerHTML = ""
    document.querySelector("#heading-view").appendChild(div)
}

// show posts
function show_all_posts(page_num = 1, username = "", following = "") {

    //store values
    sessionStorage.setItem('g_page_num', page_num)
    sessionStorage.setItem('g_username', username)
    sessionStorage.setItem('g_following', following)

    // all posts
    if (username == "" && following != 1) {
        change_heading("All Posts")
        try { document.querySelector("#profile-view").style.display = "none" } catch (err) { }
        try { document.querySelector("#new-post-view").style.display = "block" } catch (err) { }
    }

    // single person posts
    if (username != "" && following != 1) {
        show_profile(username)
    }

    //following posts
    if (following == 1) {
        change_heading("Following")
        try { document.querySelector("#profile-view").style.display = "none" } catch (err) { }
        try { document.querySelector("#new-post-view").style.display = "none" } catch (err) { }
        username = document.querySelector("#login_user").value
    }

    fetch("/all_posts/" + page_num + "/" + username + "/" + following, { method: "GET" })
        .then(response => response.json())
        .then(r => {
            var results = r.data
            var page_num = results[0]
            var num_pages = results[1]
            var posts = results[2]
            var prev = ""
            var next = ""

            //add previous page button
            if (page_num != 1) {
                var prev = document.createElement("button")
                prev.className = "btn btn-sm btn-outline-primary"
                prev.innerHTML = "Previous"
                prev.addEventListener("click", () => show_all_posts(page_num - 1, username, following))
            }

            //add next page button
            if (page_num < num_pages) {
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
        // create view container
        var view = document.createElement("div")
        view.className = "single-post-view"
        document.querySelector("#all-posts-view").appendChild(view)

        // add username
        var user = document.createElement("div")
        user.innerHTML = p[1].bold()
        if (1/*document.querySelector("#username")*/) {  // allow profile page view only if logged in
            user.addEventListener("click", function () {
                show_all_posts(1, p[1])  //go to profile
            })
        }
        view.appendChild(user)

        // add post content
        var body = document.createElement("div")
        body.innerHTML = p[2]
        view.appendChild(body)
        var likes_time = document.createElement("div")
        view.appendChild(likes_time)

        var login_user
        try { login_user = document.querySelector("#username").innerHTML } catch (err) { }

        // if logged in , add like button , add like stats
        if (login_user) {
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
                        var num_like = likes_time.innerHTML.replace("<b>", "").split(" ")[0]
                        if (results.message === "like created") {
                            num_like++
                            like_button.innerHTML = "Unlike"
                        } else if (results.message === "like deleted") {
                            num_like--
                            like_button.innerHTML = "Like"
                        }
                        var ts = likes_time.innerHTML.split(" ")[2]
                        likes_time.innerHTML = "<b>" + num_like + " Likes</b> " + ts
                    })
            })
            view.appendChild(like_button)

            //update like button state
            fetch("/like", { method: "POST", body: JSON.stringify({ post_id: p[0], toggle: 0 }) })
                .then(response => response.json())
                .then(r => { if (r.user_like) { like_button.innerHTML = "Unlike" } })

            //if poster is user, also add edit button
            if (login_user === p[1]) {
                var edit = document.createElement("button")
                edit.className = "btn btn-sm btn-outline-primary"
                edit.innerHTML = "Edit"
                edit.addEventListener("click", function () {//edit post
                    var edit_box = document.createElement("textarea")
                    edit_box.className = "form-control"
                    edit_box.id = "edit-box"
                    edit_box.value = p[2]
                    body.innerHTML = ""
                    body.appendChild(edit_box)
                    edit.innerHTML = "Update"
                    edit.addEventListener("click", function () {
                        fetch("/new_post", {
                            method: "POST",
                            body: JSON.stringify({
                                body: edit_box.value,
                                existing_post: p[0]
                            })
                        }).then(response => {
                            location.reload()
                        })
                    })
                })
                view.appendChild(edit)
            }

        }

        //update like stats - also available to non-login users
        fetch("/like_stats/" + p[0], { method: "GET" })
            .then(response => response.json())
            .then(r => { //r[0] num of likes
                likes_time.innerHTML = "<b>" + r.num_likes + " Likes</b> " + p[3].toString() //how many times post is liked
            })

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
            body: document.querySelector("#new-post-textarea").value,
            existing_post: -1
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
            element.style.animationPlayState = "running"
            document.querySelector("#new-post-textarea").value = ""
            show_all_posts(1)
        })
}

// show profile page
function show_profile(profile_user) {
    change_heading(profile_user)
    try { document.querySelector("#profile-view").style.display = "block" } catch (err) { }
    try { document.querySelector("#new-post-view").style.display = "none" } catch (err) { }



    // get follow info
    fetch("/follow_stats/" + profile_user, { method: "GET", })
        .then(response => response.json())
        .then(r => {
            //show number of followers / following
            document.querySelector("#followers-view").innerHTML = r.num_followers + " Followers"
            document.querySelector("#following-view").innerHTML = r.num_following + " Following"

            // make follow button if logged in and profile not same person
            var login_user
            try { login_user = document.querySelector("#username").innerHTML } catch (err) { }
            if (login_user && login_user != profile_user) {
                var button = document.createElement("button")
                button.className = "btn btn-sm btn-outline-primary"
                button.id = "toggle-follow"
                fetch("/follow", {
                    method: "POST",
                    body: JSON.stringify({ followee: profile_user, toggle: 0 })
                }).then(response => response.json())
                    .then(result => {
                        if (result.message === "pair exists") {
                            document.querySelector("#heading-view").innerHTML = profile_user +
                                "&nbsp;&nbsp;&nbsp;&nbsp;<span id=\"follow-span\"><i>following</i></span>"
                            button.innerHTML = "Unfollow"
                        } else {
                            button.innerHTML = "Follow"
                        }
                    })

                // attach button and button action
                try { document.querySelector("#follow-button").innerHTML = "" } catch (err) { }
                document.querySelector("#follow-button").appendChild(button)
                button.addEventListener("click", () => {
                    fetch("/follow", {
                        method: "POST",
                        body: JSON.stringify({ followee: profile_user, toggle: 1 })
                    }).then(response => response.json())
                        .then(result => {
                            show_profile(profile_user)
                        })
                })
            }
        })
}