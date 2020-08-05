//global vars
var first_mover = "X"
var start_time = new Date().getTime()
var is_first_move = true

//squares and winning lines
var TL, TM, TR, ML, MM, MR, BL, BM, BR
var top_r, mid_r, bot_r
var left_c, mid_c, right_c
var dn_d, up_d
var combos, all_squares

const xx = '✕' //"&#10005;"
const oo = '○' //"&#9675;"

//direct button to functions
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed")

    //all posts
    try { document.querySelector("#top-left").addEventListener("click", () => square_clicked("#top-left")) } catch (err) { }
    try { document.querySelector("#top-mid").addEventListener("click", () => square_clicked("#top-mid")) } catch (err) { }
    try { document.querySelector("#top-right").addEventListener("click", () => square_clicked("#top-right")) } catch (err) { }

    try { document.querySelector("#mid-left").addEventListener("click", () => square_clicked("#mid-left")) } catch (err) { }
    try { document.querySelector("#mid-mid").addEventListener("click", () => square_clicked("#mid-mid")) } catch (err) { }
    try { document.querySelector("#mid-right").addEventListener("click", () => square_clicked("#mid-right")) } catch (err) { }

    try { document.querySelector("#bot-left").addEventListener("click", () => square_clicked("#bot-left")) } catch (err) { }
    try { document.querySelector("#bot-mid").addEventListener("click", () => square_clicked("#bot-mid")) } catch (err) { }
    try { document.querySelector("#bot-right").addEventListener("click", () => square_clicked("#bot-right")) } catch (err) { }

    try { document.querySelector("#single").addEventListener("click", () => start("Single Player")) } catch (err) { }
    try { document.querySelector("#two-p").addEventListener("click", () => start("Two Players")) } catch (err) { }
    try { document.querySelector("#reset").addEventListener("click", () => reset()) } catch (err) { }

    try { reset() } catch (err) { }
})

//mark a square
function square_clicked(button_id) {
    if (document.querySelector("#message_a").innerHTML != "Single Player" &&
        document.querySelector("#message_a").innerHTML != "Two Players") { return }
    if (document.querySelector("#message_b").innerHTML != "Turn: X" &&
        document.querySelector("#message_b").innerHTML != "Turn: O") { return }
    if (document.querySelector(button_id).innerHTML != " ") { return }
    const mode = document.querySelector("#message_a").innerHTML
    const turn = document.querySelector("#message_b").innerHTML

    if (is_first_move) {
        start_time = new Date().getTime()
        is_first_move = false
    }

    if (turn == "Turn: X") {
        document.querySelector(button_id).innerHTML = xx
        if (check_state(button_id, turn)) { return }
        else {
            document.querySelector("#message_b").innerHTML = "Turn: O"
            if (mode == "Single Player" && first_mover == "X") { setTimeout(cpu_move, 100) }
        }
    } else if (turn == "Turn: O") {
        document.querySelector(button_id).innerHTML = oo
        if (check_state(button_id, turn)) { return }
        else {
            document.querySelector("#message_b").innerHTML = "Turn: X"
            if (mode == "Single Player" && first_mover == "O") { setTimeout(cpu_move, 100) }
        }
    }
}

//cpu makes a move
function cpu_move() {

    var cpu = oo
    var player = xx
    if (first_mover == "O") {
        cpu = xx
        player = oo
    }

    refresh_state()

    //take win if available
    for (i = 0; i < combos.length; i++) {
        var line = combos[i]
        let cnt_cpu = 0
        let cnt_blank = 0
        for (j = 0; j < line.length; j++) {
            if (line[j].innerHTML === cpu) { cnt_cpu++ }
            if (line[j].innerHTML === " ") { cnt_blank++ }
        }
        if (cnt_cpu == 2 && cnt_blank == 1) {
            for (k = 0; k < line.length; k++) {
                if (line[k].innerHTML === " ") {
                    square_clicked("#" + line[k].id)
                    return
                }
            }
        }
    }

    //block if players next move will win
    for (i = 0; i < combos.length; i++) {
        var line = combos[i]
        let cnt_player = 0
        let cnt_blank = 0
        for (j = 0; j < line.length; j++) {
            if (line[j].innerHTML === player) { cnt_player++ }
            if (line[j].innerHTML === " ") { cnt_blank++ }
        }
        if (cnt_player === 2 && cnt_blank === 1) {
            for (k = 0; k < line.length; k++) {
                if (line[k].innerHTML === " ") {
                    square_clicked("#" + line[k].id)
                    return
                }
            }
        }
    }

    //take move at center if available
    if (document.querySelector("#mid-mid").innerHTML == " ") {
        square_clicked("#mid-mid")
        return
    }

    //take move a one corner with most open lanes (3 max: horz, vert, diag)
    var lanes = [top_r, left_c, dn_d, right_c, up_d, bot_r]
    var lanes_pt = {}
    for (i = 0; i < lanes.length; i++) {
        var line = lanes[i]
        for (j = 0; j < line.length; j++) {
            if (line[j].innerHTML == player) {
                lanes_pt[i] = (lanes_pt[i] || 0) - 1 //reduce pt of line with more player marks
            } else {
                lanes_pt[i] = (lanes_pt[i] || 0)
            }
        }
    }
    var corners = [TL, TR, BL, BR]
    var corner_w_pt = {} //get pt value of each corner, add small random num to end of each point set to make unique
    corner_w_pt[lanes_pt[0] + lanes_pt[1] + lanes_pt[2] + Math.ceil(Math.random() * 10) / 100] = 0 //TL
    corner_w_pt[lanes_pt[0] + lanes_pt[3] + lanes_pt[4] + Math.ceil(Math.random() * 10) / 100] = 1 //TR
    corner_w_pt[lanes_pt[5] + lanes_pt[1] + lanes_pt[4] + Math.ceil(Math.random() * 10) / 100] = 2 //BL
    corner_w_pt[lanes_pt[5] + lanes_pt[3] + lanes_pt[2] + Math.ceil(Math.random() * 10) / 100] = 3 //BR
    pt_list = Object.keys(corner_w_pt).sort((a, b) => b - a); //point list high to low
    for (i = 0; i < pt_list.length; i++) {
        let corner_key = corner_w_pt[pt_list[i]]
        if (corners[corner_key].innerHTML == " ") { //mark the corner w highest pt value
            square_clicked("#" + corners[corner_key].id)
            return
        }
    }

    //take a random corner
    corners_shuffle = corners.sort(() => Math.random() - 0.5)
    for (i = 0; i < corners_shuffle.length; i++) {
        if (corners_shuffle[i].innerHTML == " ") {
            square_clicked("#" + corners_shuffle[i].id)
            return
        }
    }

    //make a random move
    var randomItem
    while (true) {
        randomItem = all_squares[Math.floor(Math.random() * all_squares.length)];
        if (randomItem.innerHTML == " ") {
            square_clicked("#" + randomItem.id)
            return
        }
    }
}

//clear the board
function clear_board() {
    for (i = 0; i < 9; i++) {
        //console.log(document.getElementsByClassName("xo")[i].innerHTML)
        document.getElementsByClassName("tic-square")[i].innerHTML = " "
        document.getElementsByClassName("tic-square")[i].style.color = "black"
    }
}

//start the game
function start(mode) {
    clear_board()
    document.querySelector("#message_a").innerHTML = mode
    document.querySelector("#message_b").innerHTML = "Turn: " + first_mover
    document.querySelector("#single").style.display = "none"
    document.querySelector("#two-p").style.display = "none"
    document.querySelector("#reset").style.display = "inline-block"
}

//reset the game
function reset() {
    clear_board()
    document.querySelector("#message_a").innerHTML = "Select Mode"
    document.querySelector("#message_b").innerHTML = ""
    document.querySelector("#single").style.display = "inline-block"
    document.querySelector("#two-p").style.display = "inline-block"
    document.querySelector("#reset").style.display = "none"
}

//update the state of the squares
function refresh_state() {

    //squares and winning lines
    TL = document.querySelector("#top-left")
    TM = document.querySelector("#top-mid")
    TR = document.querySelector("#top-right")

    ML = document.querySelector("#mid-left")
    MM = document.querySelector("#mid-mid")
    MR = document.querySelector("#mid-right")

    BL = document.querySelector("#bot-left")
    BM = document.querySelector("#bot-mid")
    BR = document.querySelector("#bot-right")

    top_r = [TL, TM, TR]
    mid_r = [ML, MM, MR]
    bot_r = [BL, BM, BR]

    left_c = [TL, ML, BL]
    mid_c = [TM, MM, BM]
    right_c = [TR, MR, BR]

    dn_d = [TL, MM, BR]
    up_d = [BL, MM, TR]

    combos = [top_r, mid_r, bot_r, left_c, mid_c, right_c, dn_d, up_d]
    all_squares = [TL, TM, TR, ML, MM, MR, BL, BM, BR]

}

//check for match ending conditions
function check_state(button_id, turn) {
    var mark = document.querySelector(button_id)

    refresh_state()
    //check for winner
    for (i = 0; i < combos.length; i++) {
        line = combos[i]
        if (line.includes(mark)) {
            if (line[0].innerHTML == line[1].innerHTML && line[1].innerHTML == line[2].innerHTML) {
                line.forEach(square => { square.style.color = "green" })
                game_stop(turn)
                return true
            }
        }
    }

    //check if all squares are filled
    for (i = 0; i < all_squares.length; i++) {
        sq = all_squares[i]
        if (sq.innerHTML == " ") {
            return false //keep playing if not filled
        }
    }
    game_stop() //stop game if all filled
    return true
}


//annouce winner and record results
function game_stop(turn = " ") {
    var duration = new Date().getTime() - start_time
    var winner = "draw"
    if (turn == "Turn: O") {
        document.querySelector("#message_b").innerHTML = "O Won!"
        winner = "O"
    } else if (turn == "Turn: X") {
        document.querySelector("#message_b").innerHTML = "X Won!"
        winner = "X"
    } else {
        document.querySelector("#message_b").innerHTML = "Draw!"
    }

    mode = "unknown"
    if (document.querySelector("#message_a").innerHTML == "Two Players") {
        mode = "2P"
    } else if (document.querySelector("#message_a").innerHTML == "Single Player") {
        mode = "1P"
    }

    is_first_move = true

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
    fetch("/result", {
        headers: { 'X-CSRFToken': csrftoken },
        method: "POST",
        body: JSON.stringify({
            duration: duration,
            first_mover: first_mover, //global var
            mode: mode,
            winner: winner,
        })
    }).then(response => response.json())
        .then(results => { })
}