// Data Variables
let container_menu = document.querySelector(".container-menu");
let game_start = document.querySelector(".start_game");
let rules_btn = document.querySelector("#rules");
let instructions = document.querySelector(".instructions");
let back_btn_rules = document.querySelector(".back-btn");
let backgame_btn = document.querySelector(".backgame-btn")
let start_btn = document.querySelector("#start");
let timerDisplay = document.querySelector(".time");
const playerNameInput = document.querySelector("#playerNameInput");
const easyButton = document.querySelector(".btn.easy");
const hardButton = document.querySelector(".btn.hard");
const winAnimation = document.querySelector("#winAnimation");
const leaderboardContainer = document.querySelector("#leaderboard");
const leaderboardList = document.querySelector("#leaderboardList");
const showLeaderboardButton = document.querySelector("#showLeaderboard");
const closeLeaderboardButton = document.querySelector("#closeLeaderboard");
const resetLeaderboardButton = document.querySelector("#resetLeaderboard");
const insideName = document.querySelector(".designer");
let resetButton = document.querySelector("#resetButton");
let saveGameButton = document.querySelector("#saveGameButton")
let originalLayout = null;
let selectedTile = null;
let timer = null;
let startTime;
let selectedDifficulty = null;
let playerName = "";




// Timers for game, timer start krne ke liay....
function startTimer() {
    startTime = new Date();
    timer = setInterval(function () {
        const elapsedTime = new Date() - startTime;
        const seconds = Math.floor((elapsedTime / 1000) % 60);
        const minutes = Math.floor((elapsedTime / 1000 / 60) % 60);
        timerDisplay.textContent = formatTime(minutes) + ':' + formatTime(seconds);

        const isWin = checkWinCondition(getCurrentBoardLayout());
        console.log("Win Condition Check:", isWin);
        if (isWin) {
            stopTimer();
            displayWinAnimation(minutes, seconds);
        }
    }, 500);
}

// Time ko format krnaa
function formatTime(time) {
    return time < 10 ? '0' + time : time;
}
// Stop timer, jo ke time ko stop krega
function stopTimer() {
    clearInterval(timer);
}
// Reset timer jo ke time ko reset krega jeetnay pr
function resetTimer() {
    stopTimer();
    timerDisplay.textContent = "00:00";
    startTimer();
}


// Game Maps Data
const mapData = {
    "bridge": { name: "Bridge", angle: 0, src: "Images/bridge.png" },
    "empty": { name: "Empty Tile", angle: 0, src: "Images/empty.png" },
    "mountain": { name: "Mountain", angle: 0, src: "Images/mountain.png" },
    "oasis": { name: "Oasis", angle: 0, src: "Images/oasis.png" },
    "straight_rail": { name: "Straight Rail", angle: 0, src: "Images/straight_rail.png" },
    "curve_rail": { name: "Curve Rail", angle: 0, src: "Images/curve_rail.png" },
    "mountain_rail": { name: "Mountain Rail", angle: 0, src: "Images/mountain_rail.png" },
    "bridge_rail": { name: "Bridge Rail", angle: 0, src: "Images/bridge_rail.png" }
};
// Layouts for 5
const layout_5_1 = [
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 180 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }, { type: "oasis", angle: 180 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 180 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }]
];
const layout_5_2 = [
    [{ type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 180 }],
    [{ type: "bridge", angle: 0 }, { type: "oasis", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 180 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }]
];
const layout_5_3 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 180 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 180 }]
];
const layout_5_4 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 180 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 90 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }]
];
const layout_5_5 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }]
];

// Layouts for 7 
const layout_7_1 = [
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "oasis", angle: 90 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "mountain", angle: 270 }, { type: "empty", angle: 180 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 90 }, { type: "oasis", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 180 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }]
];
const layout_7_2 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "mountain", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }]
];
const layout_7_3 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }],
    [{ type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }]
];
const layout_7_4 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 900 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "bridge", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 270 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 90 }, { type: "empty", angle: 0 }]
];
const layout_7_5 = [
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "bridge", angle: 90 }, { type: "bridge", angle: 90 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 90 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "mountain", angle: 0 }, { type: "empty", angle: 0 }, { type: "oasis", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "mountain", angle: 180 }, { type: "empty", angle: 0 }, { type: "bridge", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }],
    [{ type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }, { type: "empty", angle: 0 }]
];
// All 5 layeouts
const layouts_5 = [
    layout_5_1,
    layout_5_2,
    layout_5_3,
    layout_5_4,
    layout_5_5,
];
// All 7 layouts
const layouts_7 = [
    layout_7_1,
    layout_7_2,
    layout_7_3,
    layout_7_4,
    layout_7_5,
];

let bestLayout = null; 
// Random Layout nikalnay ke liay.
function getRandomLayout() {
    const randomIndex = Math.floor(Math.random() * 5);
    return bestLayout[randomIndex];
}
// Message box jo ke game ke doran msg dega
const messageBox = document.querySelector("#messageBox");
function showMessage(message) {
    messageBox.innerText = message;
    messageBox.style.display = "block";
    setTimeout(() => {
        messageBox.style.display = "none"; 
    }, 3000);
}

// Msg box jo main screen pr errors ya msgs dega
const mainScreenMessageBox = document.querySelector("#main_screen_msg_box");
function showMainScreenMessage(message) {
    mainScreenMessageBox.innerText = message;
    mainScreenMessageBox.style.display = "block"; 
    setTimeout(() => {
        mainScreenMessageBox.style.display = "none"; 
    }, 3000);
}
// Main function haa jo ke board ko populate kraygaa, right click pr delete or left pr rotate krayga.
function populateGameBoard(layout) {
    const gameBoard = document.querySelector("#gameBoard");

    gameBoard.innerHTML = '';

    layout.forEach((rowData, rowIndex) => {
        const row = document.createElement('tr');
        rowData.forEach((tile, colIndex) => {
            const cell = document.createElement('td');
            const tileData = mapData[tile.type];
            const imgElement = document.createElement('img');
            imgElement.src = tileData.src;
            imgElement.alt = tileData.name;
            imgElement.style.transform = `rotate(${tile.angle}deg)`;
            cell.appendChild(imgElement);
            row.appendChild(cell);


            imgElement.addEventListener('contextmenu', function (event) {
                event.preventDefault(); 
                restoreTileIfDifferent(rowIndex, colIndex, imgElement);
            });

            imgElement.addEventListener('click', function (event) {
                if (!imgElement.hasAttribute("data-click-count")) {
                    imgElement.setAttribute("data-click-count", 0);
                }

                let clickCount = parseInt(imgElement.getAttribute("data-click-count"));

                if (clickCount === 0) {
                    if (selectedTile) {
                        const currentTileType = tile.type;
                        const selectedTileType = selectedTile.name;

                        let canReplace = false;
                        if (currentTileType === "empty" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
                            canReplace = true;
                        } else if (currentTileType === "straight_rail" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
                            canReplace = true;
                        } else if (currentTileType === "curve_rail" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
                            canReplace = true;
                        } else if (currentTileType === "bridge" && selectedTileType === "bridge_rail") {
                            canReplace = true;
                        } else if (currentTileType === "mountain" && selectedTileType === "mountain_rail") {
                            canReplace = true;
                        }

                        if (canReplace) {
                            imgElement.src = selectedTile.src;
                            imgElement.alt = selectedTile.name;

                            if (selectedTileType !== "bridge_rail" && selectedTileType !== "mountain_rail") {
                                imgElement.style.transform = `rotate(${selectedTile.angle}deg)`;
                            } else {
                                imgElement.style.transform = `rotate(${tile.angle}deg)`;
                            }

                            imgElement.setAttribute("data-click-count", clickCount + 1);
                        }
                    }
                } else {
                    if (selectedTile && selectedTile.name !== "bridge_rail" && selectedTile.name !== "mountain_rail") {
                        selectedTile.angle = (selectedTile.angle + 90) % 360;
                        imgElement.style.transform = `rotate(${selectedTile.angle}deg)`;
                    }

                    imgElement.setAttribute("data-click-count", clickCount + 1);
                }

                event.stopPropagation();
            });

            setupDragPlacement(cell, rowIndex, colIndex);
        });
        gameBoard.appendChild(row);
    });
}
// For mouse drag and drop together with mouse movement.
let isMouseDown = false;
function setupDragPlacement(cell, rowIndex, colIndex) {
    cell.addEventListener("mousedown", function (event) {
        event.preventDefault();
        isMouseDown = true;
        applyTileToCell(cell, rowIndex, colIndex);
    });

    cell.addEventListener("mouseup", function () {
        isMouseDown = false;
    });

    cell.addEventListener("mousemove", function () {
        if (isMouseDown) {
            applyTileToCell(cell, rowIndex, colIndex);
        }
    });

    cell.addEventListener("dragover", function (event) {
        event.preventDefault();
    });

    cell.addEventListener("drop", function (event) {
        event.preventDefault();
        if (selectedTile) {
            applyTileToCell(cell, rowIndex, colIndex);
        }
    });
}
// Mouse Drag drop ko implement krne liay, helper function.
function applyTileToCell(cell, rowIndex, colIndex) {
    if (!selectedTile) {
        return;
    }
    const currentTileType = getCurrentBoardLayout()[rowIndex][colIndex].type;
    const selectedTileType = selectedTile.name;

    let canReplace = false;

    if (currentTileType === "empty" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
        canReplace = true;
    } else if (currentTileType === "bridge" && selectedTileType === "bridge_rail") {
        canReplace = true;
    } else if (currentTileType === "mountain" && selectedTileType === "mountain_rail") {
        canReplace = true;
    } else if (currentTileType === "straight_rail" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
        canReplace = true;
    } else if (currentTileType === "curve_rail" && (selectedTileType === "straight_rail" || selectedTileType === "curve_rail")) {
        canReplace = true;
    } else if (currentTileType === "mountain_rail" && selectedTileType === "mountain_rail") {
        canReplace = true;
    } else if (currentTileType === "bridge_rail" && selectedTileType === "bridge_rail") {
        canReplace = true;
    }

    if (canReplace) {
        cell.querySelector('img').src = selectedTile.src;
        cell.querySelector('img').alt = selectedTile.name;
        console.log(`Tile applied at (${rowIndex}, ${colIndex})`);
    } else {
        showMessage("Invalid move: Cannot replace this tile!");
    }

}

//Function to delete tile and get old tile , jo ke populate board main use hoga.
function restoreTileIfDifferent(rowIndex, colIndex, imgElement) {
    const currentTile = getCurrentBoardLayout()[rowIndex][colIndex];
    const originalTile = originalLayout[rowIndex][colIndex]; 

    if (currentTile.type !== originalTile.type || currentTile.angle !== originalTile.angle) {
        const tileData = mapData[originalTile.type];
        imgElement.src = tileData.src;
        imgElement.alt = tileData.name;
        imgElement.style.transform = `rotate(${originalTile.angle}deg)`;
        console.log(`Tile at row ${rowIndex}, column ${colIndex} restored to original.`);
    }
}

// Function to get layer of board present condition for debugging and other purposes, jo ke board layout extratc krega
function getCurrentBoardLayout() {
    const gameBoard = document.querySelector("#gameBoard");

    const rows = gameBoard.querySelectorAll('tr');

    const currentLayout = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td');
        return Array.from(cells).map(cell => {
            const img = cell.querySelector('img');
            if (img) {
                const type = img.alt.includes("rail") ? img.alt : Object.keys(mapData).find(key => mapData[key].name === img.alt) || "empty";
                const angleMatch = img.style.transform.match(/rotate\((\d+)deg\)/);
                const angle = angleMatch ? parseInt(angleMatch[1], 10) % 360 : 0;

                // Debugging output to inspect each cell's properties, debyug log ha yeh
                // console.log("Checking Cell:", cell);
                // console.log("Image Source:", img.src);
                // console.log("Image Alt (Type):", img.alt);
                // console.log("Determined Type:", type);
                // console.log("Rotation Angle:", angle);

                return { type: type, angle: angle };
            } else {
                return { type: "empty", angle: 0 }; 
            }
        });
    });

    console.log("Current Board Layout:", currentLayout); 
    return currentLayout;
}

// printing board layout to check or for check purposes or debugging, to check purposes.
function printCurrentBoardLayout() {
    const layout = getCurrentBoardLayout();
    console.log("Current Board Layout:");
    console.log(layout);
}

// To check ans whether ans is right or not or layouts are equal or not for checking
function layoutsAreEqual(layout1, layout2) {
    if (layout1.length !== layout2.length) return false;
    for (let i = 0; i < layout1.length; i++) {
        if (layout1[i].length !== layout2[i].length) return false;
        for (let j = 0; j < layout1[i].length; j++) {
            if (layout1[i][j].type !== layout2[i][j].type || layout1[i][j].angle !== layout2[i][j].angle) {
                console.log(`Mismatch at row ${i}, column ${j}: Expected { type: ${layout2[i][j].type}, angle: ${layout2[i][j].angle} }, Found { type: ${layout1[i][j].type}, angle: ${layout1[i][j].angle} }`);
                return false;
            }
        }
    }
    return true;
}


// To check win condition or whether the map is completed or not, a data strcuture for checking
const railProperties = {
    straight_rail: {
        0: ["top", "bottom"],
        90: ["left", "right"],
        180: ["top", "bottom"],
        270: ["left", "right"]
    },
    curve_rail: {
        0: ["bottom", "right"],
        90: ["bottom", "left"],
        180: ["top", "left"],
        270: ["top", "right"]
    },
    mountain_rail: {
        0: ["bottom", "right"],
        90: ["bottom", "left"],
        180: ["top", "left"],
        270: ["top", "right"]
    },
    bridge_rail: {
        0: ["top", "bottom"],
        180: ["top", "bottom"],
        270: ["left", "right"],
        90: ["left", "right"]
    }
};
// to check whether all the entries in board is completed or not
function isCompleteBoard(boardLayout) {
    for (let rowIndex = 0; rowIndex < boardLayout.length; rowIndex++) {
        for (let colIndex = 0; colIndex < boardLayout[rowIndex].length; colIndex++) {
            const tile = boardLayout[rowIndex][colIndex];
            if (tile.type !== "oasis" && !tile.type.includes("rail")) {
                console.log(`Tile at (${rowIndex}, ${colIndex}) is not a rail or oasis:`, tile);
                return false; // Found a non-oasis tile that isn't a rail
            }
        }
    }
    console.log("All non-oasis tiles are correctly replaced by rails.");
    return true; 
}

// to check rails are connected, connection check krne wala function
function areRailsConnected(boardLayout) {
    const rows = boardLayout.length;
    const cols = boardLayout[0].length;

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const tile = boardLayout[i][j];

            if (!tile.type.includes("rail")) continue; 

            if (!railProperties[tile.type] || !railProperties[tile.type][tile.angle]) {
                console.error(`No connection data for tile at (${i}, ${j}) with type: ${tile.type} and angle: ${tile.angle}`);
                continue;
            }

            const connections = railProperties[tile.type][tile.angle];
            console.log(`Checking connections for rail at (${i}, ${j}) with type: ${tile.type} and angle: ${tile.angle}`);
            console.log(`Current tile connections: ${connections.join(', ')}`);

            if (connections.includes("top") && i > 0) {
                const topTile = boardLayout[i - 1][j];
                if (topTile && railProperties[topTile.type] && railProperties[topTile.type][topTile.angle]) {
                    const topTileConnections = railProperties[topTile.type][topTile.angle];
                    const topConnected = topTile.type.includes("rail") && topTileConnections.includes("bottom");

                    console.log(`Top neighbor at (${i - 1}, ${j}) - Type: ${topTile.type}, Angle: ${topTile.angle}`);
                    console.log(`Top neighbor connections: ${topTileConnections.join(', ')} - Connected: ${topConnected}`);

                    if (!topConnected) return false;
                }
            }

            if (connections.includes("bottom") && i < rows - 1) {
                const bottomTile = boardLayout[i + 1][j];
                if (bottomTile && railProperties[bottomTile.type] && railProperties[bottomTile.type][bottomTile.angle]) {
                    const bottomTileConnections = railProperties[bottomTile.type][bottomTile.angle];
                    const bottomConnected = bottomTile.type.includes("rail") && bottomTileConnections.includes("top");

                    console.log(`Bottom neighbor at (${i + 1}, ${j}) - Type: ${bottomTile.type}, Angle: ${bottomTile.angle}`);
                    console.log(`Bottom neighbor connections: ${bottomTileConnections.join(', ')} - Connected: ${bottomConnected}`);

                    if (!bottomConnected) return false;
                }
            }

            if (connections.includes("left") && j > 0) {
                const leftTile = boardLayout[i][j - 1];
                if (leftTile && railProperties[leftTile.type] && railProperties[leftTile.type][leftTile.angle]) {
                    const leftTileConnections = railProperties[leftTile.type][leftTile.angle];
                    const leftConnected = leftTile.type.includes("rail") && leftTileConnections.includes("right");

                    console.log(`Left neighbor at (${i}, ${j - 1}) - Type: ${leftTile.type}, Angle: ${leftTile.angle}`);
                    console.log(`Left neighbor connections: ${leftTileConnections.join(', ')} - Connected: ${leftConnected}`);

                    if (!leftConnected) return false;
                }
            }

            if (connections.includes("right") && j < cols - 1) {
                const rightTile = boardLayout[i][j + 1];
                if (rightTile && railProperties[rightTile.type] && railProperties[rightTile.type][rightTile.angle]) {
                    const rightTileConnections = railProperties[rightTile.type][rightTile.angle];
                    const rightConnected = rightTile.type.includes("rail") && rightTileConnections.includes("left");

                    console.log(`Right neighbor at (${i}, ${j + 1}) - Type: ${rightTile.type}, Angle: ${rightTile.angle}`);
                    console.log(`Right neighbor connections: ${rightTileConnections.join(', ')} - Connected: ${rightConnected}`);

                    if (!rightConnected) return false;
                }
            }
        }
    }
    console.log("All rails are correctly connected.");
    return true; 
}

// checking both rails and tiles conditions overall map checker or win checker
function checkWinCondition(boardLayout) {
    const completeBoard = isCompleteBoard(boardLayout);
    console.log("Complete Board Check:", completeBoard);

    const railsConnected = areRailsConnected(boardLayout);
    console.log("Rails Connected Check:", railsConnected);

    const winCondition =completeBoard && railsConnected;
    console.log("Win Condition:", winCondition);
    return winCondition;
}

// function that will reset the board to its initial state, that reset my board, board ko reset krega
function resetBoard() {
    populateGameBoard(originalLayout);
    showMessage("Board has been reset.")
}

// making reset button, board reset krne wala button
if (resetButton) {
    resetButton.addEventListener("click", resetBoard);
}

//function to reset everything,  sab kuch reset krdega, sabko initial halat main lanay wala button
function resetEverything() {
    container_menu.hidden = false;
    game_start.hidden = true;
    selectedTile = null;
    selectedDifficulty = null;
    bestLayout = null;
    playerNameInput.value = "";
    insideName.textContent = "Player";
    timerDisplay.textContent = "00:00";

    easyButton.classList.remove("selected");
    hardButton.classList.remove("selected");

    stopTimer();

    localStorage.removeItem("savedGameState");
    localStorage.removeItem("originalLayout");
    localStorage.removeItem("playerName");

    if (originalLayout) {
        populateGameBoard(originalLayout);
    } else {
        resetBoard();
    }

    console.log("Game has been reset.");
}

const paletteImages = document.querySelectorAll(".palette-image");
let currentPaletteIndex = 0; 
// function for using arrow keys for selection of palettes, bonus point ha yeh

function updateActivePalette(index) {
    paletteImages.forEach((img) => img.classList.remove("active-palette"));

    const img = paletteImages[index];
    img.classList.add("active-palette");

    selectedTile = {
        src: img.src,
        name: img.alt.includes("rail") ? img.alt : "",
        angle: 0
    };
}
updateActivePalette(currentPaletteIndex);

// function to handle arrow key presses, arrow keys ka use karna hai, yeh function ka
paletteImages.forEach((img, index) => {
    img.setAttribute("data-click-count", 0);
    img.draggable = true;

    img.addEventListener("click", function () {
        currentPaletteIndex = index; 
        updateActivePalette(currentPaletteIndex); 
        let clickCount = parseInt(img.getAttribute("data-click-count"));
        img.setAttribute("data-click-count", clickCount + 1);
    });

    img.addEventListener("dragstart", function (event) {
        selectedTile = {
            src: img.src,
            name: img.alt,
            angle: 0
        };
        event.dataTransfer.setData("text/plain", img.alt);
    });
});

// function to handle arrow events, aroow keys ka use karna hai, yeh function os liay ha
document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
        currentPaletteIndex = (currentPaletteIndex + 1) % paletteImages.length;
    }else if (event.key === "ArrowUp") {
        currentPaletteIndex = (currentPaletteIndex - 1 + paletteImages.length) % paletteImages.length;
    } 
    else if (event.key === "ArrowRight") {
        currentPaletteIndex = (currentPaletteIndex - 1 + paletteImages.length) % paletteImages.length;
    } 
    else if (event.key === "ArrowLeft") {
        currentPaletteIndex = (currentPaletteIndex + 1) % paletteImages.length;
    }
    else {
        return; 
    }

    updateActivePalette(currentPaletteIndex); 
});

// Win Animation and saving scores and other thigns
function displayWinAnimation(minutes, seconds) {
    stopTimer();
    document.querySelector("#overlay").style.display = "block";
    document.querySelector("#winAnimation").style.display = "block";

    const saveScoreButton = document.querySelector("#saveScoreButton");
    saveScoreButton.onclick = function () {
        const playerName = document.querySelector("#playerNameInput").value.trim() || "Player";
        const time = formatTime(minutes) + ":" + formatTime(seconds);

        const leaderboard = JSON.parse(localStorage.getItem("leaderboard")) || [];

        leaderboard.push({ name: playerName, time: time, difficulty: selectedDifficulty });
        localStorage.setItem("leaderboard", JSON.stringify(leaderboard));

        showMainScreenMessage(`Score saved for ${playerName}! Time: ${time}`);

        document.querySelector("#winAnimation").style.display = "none";
        document.querySelector("#overlay").style.display = "none";

        const leaderboardContainer = document.querySelector("#leaderboard");
        leaderboardContainer.hidden = false;

        displayLeaderboard();

        setTimeout(() => {
            leaderboardContainer.hidden = true;
        }, 5000);
        
        resetEverything();
    };
}

// LeaderBoard, and its functions
function resetLeaderboard() {
    localStorage.removeItem("leaderboard");
    leaderboardList.innerHTML = "";
    showMainScreenMessage("Leaderboard has been reset.");
}

// fucntion jo leaderboard ko show kryga
function displayLeaderboard() {
    leaderboardList.innerHTML = ""; 

    const scores = JSON.parse(localStorage.getItem("leaderboard")) || [];

    const groupedScores = {
        "5x5": [],
        "7x7": []
    };

    scores.forEach(score => {
        if (score.difficulty === "5x5") groupedScores["5x5"].push(score);
        else if (score.difficulty === "7x7") groupedScores["7x7"].push(score);
    });

    groupedScores["5x5"].sort((a, b) => {
        const [aMinutes, aSeconds] = a.time.split(":").map(Number);
        const [bMinutes, bSeconds] = b.time.split(":").map(Number);
        return aMinutes * 60 + aSeconds - (bMinutes * 60 + bSeconds); 
    });

    groupedScores["7x7"].sort((a, b) => {
        const [aMinutes, aSeconds] = a.time.split(":").map(Number);
        const [bMinutes, bSeconds] = b.time.split(":").map(Number);
        return (bMinutes * 60 + bSeconds) - (aMinutes * 60 + aSeconds);
    });

    function createTableForDifficulty(difficulty, scores) {
        const tableContainer = document.createElement("div");
        const title = document.createElement("h3");
        title.textContent = `${difficulty} Difficulty Leaderboard`;
        tableContainer.appendChild(title);

        const table = document.createElement("table");
        table.classList.add("leaderboard-table");

        const headerRow = table.insertRow();
        headerRow.innerHTML = "<th>Rank</th><th>Name</th><th>Time</th>";

        scores.forEach((score, index) => {
            const row = table.insertRow();
            row.innerHTML = `<td>${index + 1}</td><td>${score.name}</td><td>${score.time}</td>`;
        });

        tableContainer.appendChild(table);
        leaderboardList.appendChild(tableContainer);
    }

    if (groupedScores["5x5"].length > 0) {
        createTableForDifficulty("5x5", groupedScores["5x5"]);
    }
    if (groupedScores["7x7"].length > 0) {
        createTableForDifficulty("7x7", groupedScores["7x7"]);
    }
}

// Saving Game State
function saveGameState() {
    const gameState = {
        playerName: playerNameInput.value.trim(),
        selectedDifficulty: selectedDifficulty,
        timer: timerDisplay.textContent,
        boardLayout: getCurrentBoardLayout()
    };
    localStorage.setItem("savedGameState", JSON.stringify(gameState));
    showMessage("Game has been successfully saved!");

}
// game state restorr krega
function restoreGameState() {
    const savedState = JSON.parse(localStorage.getItem("savedGameState"));
    const savedOriginalLayout = JSON.parse(localStorage.getItem("originalLayout"));
    if (savedOriginalLayout) {
        originalLayout = savedOriginalLayout;
        console.log("Restored original layout from localStorage:", originalLayout);
    } else {
        console.log("No original layout found in localStorage.");
    }

    if (savedState) {
        playerNameInput.value = savedState.playerName;
        insideName.textContent = savedState.playerName || "Player";

        selectedDifficulty = savedState.selectedDifficulty;
        timerDisplay.textContent = savedState.timer;

        initialLayout = savedState.boardLayout;
        console.log("Restoring board layout:", initialLayout);

        if (selectedDifficulty === "5x5") {
            easyButton.classList.add("selected");
            hardButton.classList.remove("selected");
            bestLayout = layouts_5;
        } else if (selectedDifficulty === "7x7") {
            hardButton.classList.add("selected");
            easyButton.classList.remove("selected");
            bestLayout = layouts_7;
        }

        container_menu.hidden = true;
        game_start.hidden = false;

        populateGameBoard(initialLayout);

        resumeTimerFromSaved(savedState.timer);
        console.log("Game state restored:", savedState);
    } else {
        console.log("No saved game state found.");
    }
}

// Game state ka timer resume krega refresh hone pr
function resumeTimerFromSaved(savedTime) {
    const [minutes, seconds] = savedTime.split(":").map(Number);
    const savedElapsedMs = (minutes * 60 + seconds) * 1000;
    startTime = new Date(new Date() - savedElapsedMs);

    timer = setInterval(function () {
        const elapsedTime = new Date() - startTime;
        const currentSeconds = Math.floor((elapsedTime / 1000) % 60);
        const currentMinutes = Math.floor((elapsedTime / 1000 / 60) % 60);
        timerDisplay.textContent = formatTime(currentMinutes) + ':' + formatTime(currentSeconds);

        if (checkWinCondition(getCurrentBoardLayout())) {
            stopTimer();
            displayWinAnimation(currentMinutes, currentSeconds);
        }
    }, 500);
}
saveGameButton.addEventListener("click", saveGameState);

restoreGameState();


// Buttons and their workings
rules_btn.addEventListener("click", function () {
    container_menu.hidden = true;
    instructions.hidden = false;
});

back_btn_rules.addEventListener("click", function () {
    container_menu.hidden = false;
    instructions.hidden = true;
});

playerNameInput.addEventListener("input", () => {
    const playerName = playerNameInput.value.trim();
    if (playerName) {
        localStorage.setItem("playerName", playerName);
        insideName.textContent = playerNameInput.value || "Player";
    }
});

easyButton.addEventListener("click", () => {
    selectedDifficulty = "5x5";
    easyButton.classList.add("selected");
    hardButton.classList.remove("selected");
    console.log("Easy button selected");
});

hardButton.addEventListener("click", () => {
    selectedDifficulty = "7x7";
    hardButton.classList.add("selected");
    easyButton.classList.remove("selected");
    console.log("Hard button selected");
});

start_btn.addEventListener("click", function () {
    const playerName = playerNameInput.value.trim();

    if (!playerName) {
        showMainScreenMessage("Please enter your name.");
        return;
    }

    if (!selectedDifficulty) {
        showMainScreenMessage("Please select a difficulty level.");
        return;
    }

    if (selectedDifficulty === "5x5") {
        bestLayout = layouts_5;
    } else {
        bestLayout = layouts_7;
    }

    initialLayout = getRandomLayout();

    originalLayout = JSON.parse(JSON.stringify(initialLayout));
    localStorage.setItem("originalLayout", JSON.stringify(originalLayout));


    container_menu.hidden = true;
    game_start.hidden = false;
    populateGameBoard(initialLayout);
    startTimer();
});

backgame_btn.addEventListener("click", () => {
    resetEverything();
})

resetLeaderboardButton.addEventListener("click", resetLeaderboard);

showLeaderboardButton.addEventListener("click", function () {
    displayLeaderboard();
    leaderboardContainer.hidden = false;
});

closeLeaderboardButton.addEventListener("click", function () {
    leaderboardContainer.hidden = true;
});

