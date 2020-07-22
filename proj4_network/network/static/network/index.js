"use strict"

// direct button to functions
document.addEventListener("DOMContentLoaded", function() {
    console.log('DOM fully loaded and parsed');
    // Add listeners to all buttons
    document.querySelector("#all-posts").addEventListener("click", () => show_all_posts())
    document.querySelector("#following").addEventListener("click", () => show_following())
    // By default, load all posts
    show_all_posts()
})

// open new post view
function change_heading(text){
    var div = document.createElement("div")
    div.innerHTML = text
    document.querySelector("#heading-view").innerHTML = ""
    document.querySelector("#heading-view").appendChild(div)
}

// open new post view
function new_post_window(){
    document.createElement("tr")
    document.querySelector("#new-post-view")
}

// show all posts
function show_all_posts(){
    change_heading("All Posts")
}

// show following
function show_following(){
    change_heading("Following")

}