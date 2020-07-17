"use strict"

// direct button to functions
document.addEventListener("DOMContentLoaded", function() {

    // Use buttons to toggle between views
    document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"))
    document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent"))
    document.querySelector("#archived").addEventListener("click", () => load_mailbox("archive"))
    document.querySelector("#compose").addEventListener("click", () => compose_email())

    // Clear the message view on any button press
    document.querySelector("#button_wrapper").addEventListener('click', (event) => {
        document.querySelector("#message-view").innerHTML = ""
    })

    // By default, load the inbox
    load_mailbox("inbox")
})

// send email button function action
function send_email() {
    // make api call
    fetch("/emails", {
            method: "POST",
            body: JSON.stringify({
                recipients: document.querySelector("#compose-recipients").value, //e.g. "byu"
                subject: document.querySelector("#compose-subject").value, //e.g "Meeting time",
                body: document.querySelector("#compose-body").value //e.g "How about we meet tomorrow at 3pm?"
            })
        })
        .then(response => response.json())
        .then(result => {
            // display result as message
            if (result.message === undefined) {
                document.querySelector("#message-view").innerHTML = result.error.italics()
            } else if (result.error === undefined) {
                document.querySelector("#message-view").innerHTML = result.message.italics()
                load_mailbox("sent")
            } else {
                document.querySelector("#message-view").innerHTML = ("Message Not Sent: Unknown Error").italics()
            }
        })
}

// compose email button action
function compose_email(recipients = "", subject = "", body = "") {

    // new email if no recipients specified, or else do a reply
    if (recipients === "") {
        document.querySelector("#compose-header").innerHTML = "New Email"
    } else {
        document.querySelector("#compose-header").innerHTML = "Reply"
    }
    // Show compose view and hide other views
    document.querySelector("#emails-view").style.display = "none"
    document.querySelector("#compose-view").style.display = "block"

    // Fill out composition fields
    document.querySelector("#compose-recipients").value = recipients
    document.querySelector("#compose-subject").value = subject
    document.querySelector("#compose-body").value = body
}

// load a mailbox of choice from button, for inbox, sent, archive buttons
function load_mailbox(mailbox) {

    // Show the mailbox and hide other views
    document.querySelector("#emails-view").style.display = "block"
    document.querySelector("#compose-view").style.display = "none"

    // Show the mailbox name
    document.querySelector("#emails-view").innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`

    // Get the emails
    fetch("/emails/" + mailbox, { method: "GET" })
        .then(response => response.json())
        .then(result => list_emails(mailbox, result))
}

// helper to display contents of a mailbox
function list_emails(mailbox, emails) {

    // Make email table
    const table = document.createElement("table")
    document.querySelector("#emails-view").append(table)

    // Make a row for each email
    for (let i = 0; i < emails.length; i++) {
        //skip if email is archived, and mailbox is not archive
        if (mailbox != "archive" && emails[i].archived) { continue }

        // build row
        const row = document.createElement("tr")
        row.id = "email_row_" + i
        if (emails[i].read === true) { row.style.backgroundColor = "lightgray" } else { row.style.fontWeight = "bold" }
        table.appendChild(row)

        // build row conents, use sender email if in inbox, use recipient if in sentbox
        var address = emails[i].sender
        if (mailbox === "sent") { address = "To: " + emails[i].recipients }
        insert_block("td", address, "#email_row_" + i)
        insert_block("td", emails[i].subject, "#email_row_" + i)
        insert_block("td", emails[i].timestamp, "#email_row_" + i)

        // clicking on the email loads the email, and marks it as read if from inbox
        row.addEventListener("click", function() {
            //if inbox, mark as read
            if (mailbox === "inbox") { fetch("/emails/" + emails[i].id, { method: "PUT", body: JSON.stringify({ read: true }) }) }
            load_email(emails[i].id, mailbox)
        })
    }
}

// helper to show a single email
function load_email(email_id, mailbox) {
    //get email by id
    fetch("/emails/" + email_id)
        .then(response => response.json())
        .then(email => {
            // empty out email view
            document.querySelector("#emails-view").innerHTML = ""

            // Build email layout
            insert_block("div", "<b>" + email.subject + "</b>", "#emails-view")
            insert_block("div", "&nbsp") //spacer

            insert_block("div", "Time: " + email.timestamp)
            insert_block("div", "From: " + email.sender)
            insert_block("div", "To: " + email.recipients)
            insert_block("div", "&nbsp")

            // add reply button
            make_reply(email)

            // add archive button
            if (mailbox === "inbox") {
                archive_button(email.id, "Archive", true)
            } else if (mailbox === "archive") { archive_button(email.id, "Unarchive", false) }

            // add body
            insert_block("div", "<hr><pre>" + email.body + "</pre>")
        })
}

// helper to make reply button{
function make_reply(email) {
    const button = document.createElement("button")
    button.className = "btn btn-sm btn-outline-primary"
    button.innerHTML = "Reply"
    button.addEventListener("click", function() {
        compose_email(email.sender, "Re: " + email.subject, "\n\n----------\nOn " +
            email.timestamp + " " + email.sender + "wrote:\n" + email.body)
    })
    document.querySelector("#emails-view").append(button)
}

// helper to make archive button{
function archive_button(email_id, name, archive_flag = false) {
    const button = document.createElement("button")
    button.className = "btn btn-sm btn-outline-primary"
    button.innerHTML = name
    button.addEventListener("click", function() {
        fetch("/emails/" + email_id, {
            method: "PUT",
            body: JSON.stringify({ archived: archive_flag })
        }).then(() => load_mailbox("inbox"))
    })
    document.querySelector("#emails-view").append(button)
}

// helper to make and insert a html block
function insert_block(type, content, view = "#emails-view") {
    const block = document.createElement(type)
    block.innerHTML = content
    document.querySelector(view).appendChild(block)
}