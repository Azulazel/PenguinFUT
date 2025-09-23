// game.js
// This file will contain the game logic for Penguin Soccer.

// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// --- Asset Loading ---
const penguinSkins = {};

function loadSkins() {
    TEAMS_DATA.forEach(team => {
        const skinImage = new Image();
        skinImage.src = `assets/skins/skin_${team.skin_id}.png`;
        penguinSkins[team.skin_id] = skinImage;
    });
}

const sounds = {
    menuNavigate: new Audio('assets/sounds/menu_navigate.wav'),
    menuSelect: new Audio('assets/sounds/menu_select.wav'),
    minigameAction: new Audio('assets/sounds/minigame_action.wav'),
    minigameWin: new Audio('assets/sounds/minigame_win.wav'),
    minigameLoss: new Audio('assets/sounds/minigame_loss.wav'),
};

// --- Team Data (from team.py) ---
const TEAMS_DATA = [
    { id: 1, name: "Red Robins", skin_id: 1, color: "rgb(255, 0, 0)" },
    { id: 2, name: "Blue Blizzards", skin_id: 2, color: "rgb(0, 0, 255)" },
    { id: 3, name: "Green Ghosts", skin_id: 3, color: "rgb(0, 255, 0)" },
    { id: 4, name: "Yellow Yaks", skin_id: 4, color: "rgb(255, 255, 0)" },
    { id: 5, name: "Purple Penguins", skin_id: 5, color: "rgb(128, 0, 128)" },
    { id: 6, name: "Orange Otters", skin_id: 6, color: "rgb(255, 165, 0)" },
    { id: 7, name: "Cyan Cyclones", skin_id: 7, color: "rgb(0, 255, 255)" },
    { id: 8, name: "Pink Panthers", skin_id: 8, color: "rgb(255, 192, 203)" },
    { id: 9, name: "Brown Bears", skin_id: 9, color: "rgb(165, 42, 42)" },
    { id: 10, name: "Grey Geese", skin_id: 10, color: "rgb(128, 128, 128)" },
    { id: 11, name: "Golden Griffins", skin_id: 11, color: "rgb(255, 215, 0)" },
    { id: 12, name: "Silver Sharks", skin_id: 12, color: "rgb(192, 192, 192)" },
    { id: 13, name: "Bronze Badgers", skin_id: 13, color: "rgb(205, 127, 50)" },
    { id: 14, name: "Navy Narwhals", skin_id: 14, color: "rgb(0, 0, 128)" },
    { id: 15, name: "Teal Turtles", skin_id: 15, color: "rgb(0, 128, 128)" },
    { id: 16, name: "Maroon Monkeys", skin_id: 16, color: "rgb(128, 0, 0)" },
    { id: 17, name: "Olive Owls", skin_id: 17, color: "rgb(128, 128, 0)" },
    { id: 18, name: "Lime Lions", skin_id: 18, color: "rgb(0, 128, 0)" },
    { id: 19, name: "Indigo Iguanas", skin_id: 19, color: "rgb(75, 0, 130)" },
    { id: 20, name: "Violet Vultures", skin_id: 20, color: "rgb(238, 130, 238)" },
];

function getTeamById(id) {
    return TEAMS_DATA.find(team => team.id === id);
}

// --- Cup Data ---
const CUP_STAGES = ["Oitavas de Final", "Quartas de Final", "Semifinal", "Final"];
const TEAMS_IN_CUP = 16;
let currentCupData = null;
let activePlayerCupMatch = null;
let currentMatchInfo = null;
let currentMinigameState = null;

const cupTeamSelection = {
    selectedTeamIndex: 0,
    scrollOffset: 0,
    teamsPerPage: 10
};

function getRandomTeams(count, exclude_teams_ids = []) {
    const availableTeams = TEAMS_DATA.filter(team => !exclude_teams_ids.includes(team.id));
    for (let i = availableTeams.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [availableTeams[i], availableTeams[j]] = [availableTeams[j], availableTeams[i]];
    }
    return availableTeams.slice(0, count);
}

// Game state
let gameState = 'main_menu';

// --- Minigame Constants ---
const MINIGAME_BAR_WIDTH = 200;
const MINIGAME_BAR_HEIGHT = 30;
const MINIGAME_TARGET_ZONE_WIDTH = 40;

// --- Game Logic Functions ---

function startQuickGame() {
    const PLAYER_DEFAULT_TEAM_ID = 1;
    const playerTeamData = getTeamById(PLAYER_DEFAULT_TEAM_ID);
    const availableOpponents = TEAMS_DATA.filter(team => team.id !== playerTeamData.id);
    const opponentTeamData = availableOpponents[Math.floor(Math.random() * availableOpponents.length)];

    currentMatchInfo = {
        player_team: playerTeamData,
        opponent_team: opponentTeamData,
        status: 'playing', // Directly start the minigame
        winner: null,
    };

    startPlayerMatchMinigame(currentMatchInfo);
    gameState = 'quick_game_active';
}

// --- Cup Logic Functions ---
function initializeCup(playerSelectedTeamId) {
    const playerTeam = getTeamById(playerSelectedTeamId);
    const numAiTeams = TEAMS_IN_CUP - 1;
    const aiTeams = getRandomTeams(numAiTeams, [playerSelectedTeamId]);
    const allCupTeams = [playerTeam, ...aiTeams];

    for (let i = allCupTeams.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allCupTeams[i], allCupTeams[j]] = [allCupTeams[j], allCupTeams[i]];
    }

    const initialMatches = [];
    for (let i = 0; i < allCupTeams.length; i += 2) {
        if (i + 1 < allCupTeams.length) {
            const team1 = allCupTeams[i];
            const team2 = allCupTeams[i + 1];
            initialMatches.push({
                team1: team1,
                team2: team2,
                winner: null,
                played: false,
                is_player_match: (team1.id === playerTeam.id || team2.id === playerTeam.id),
                match_id: `${CUP_STAGES[0]}_${initialMatches.length + 1}`
            });
        }
    }

    currentCupData = {
        player_team: playerTeam,
        current_stage_index: 0,
        stages: { [CUP_STAGES[0]]: initialMatches },
        status: 'active',
        cup_winner: null
    };

    gameState = 'cup_active';
    advanceCupStage();
}

function simulateMatch(match) {
    if (match.played) return;
    match.winner = Math.random() < 0.5 ? match.team1 : match.team2;
    match.played = true;
}

function advanceCupStage() {
    if (!currentCupData || currentCupData.status !== 'active') return;

    const currentStageName = CUP_STAGES[currentCupData.current_stage_index];
    const currentMatches = currentCupData.stages[currentStageName];

    currentMatches.forEach(match => {
        if (!match.played && !match.is_player_match) {
            simulateMatch(match);
        }
    });

    const nextPlayerMatch = getNextPlayerMatch();
    if (nextPlayerMatch) {
        activePlayerCupMatch = nextPlayerMatch;
        currentMatchInfo = {
            player_team: currentCupData.player_team,
            opponent_team: nextPlayerMatch.team1.id === currentCupData.player_team.id ? nextPlayerMatch.team2 : nextPlayerMatch.team1,
        };
        startPlayerMatchMinigame(currentMatchInfo);
        gameState = 'cup_player_match';
        return;
    }

    const allMatchesPlayed = currentMatches.every(match => match.played);

    if (allMatchesPlayed) {
        const advancingTeams = currentMatches.map(match => match.winner).filter(Boolean);

        if (advancingTeams.length === 0 && currentMatches.length > 0) {
             // This can happen if the player match was the last one. The state should transition, then advance.
             return;
        }

        if (currentCupData.current_stage_index < CUP_STAGES.length - 1) {
            currentCupData.current_stage_index++;
            const nextStageName = CUP_STAGES[currentCupData.current_stage_index];

            for (let i = advancingTeams.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [advancingTeams[i], advancingTeams[j]] = [advancingTeams[j], advancingTeams[i]];
            }

            const newMatches = [];
            for (let i = 0; i < advancingTeams.length; i += 2) {
                const team1 = advancingTeams[i];
                const team2 = advancingTeams[i+1];
                newMatches.push({
                    team1: team1,
                    team2: team2,
                    winner: null,
                    played: false,
                    is_player_match: (team1.id === currentCupData.player_team.id || team2.id === currentCupData.player_team.id),
                    match_id: `${nextStageName}_${newMatches.length + 1}`
                });
            }
            currentCupData.stages[nextStageName] = newMatches;
            // Recursively call advanceCupStage to check the new stage for player matches or simulate AI matches
            setTimeout(advanceCupStage, 500);
        } else {
            currentCupData.cup_winner = advancingTeams[0] || null;
            currentCupData.status = 'finished';
            gameState = 'cup_finished';
        }
    }
}

function getNextPlayerMatch() {
    if (!currentCupData) return null;
    const currentStageName = CUP_STAGES[currentCupData.current_stage_index];
    if (!currentCupData.stages[currentStageName]) return null;
    return currentCupData.stages[currentStageName].find(match => match.is_player_match && !match.played);
}


function startPlayerMatchMinigame(matchInfo) {
    const barStartX = (canvas.width - MINIGAME_BAR_WIDTH) / 2;
    const targetZonePercentageStart = Math.floor(Math.random() * (65 - 15 + 1)) + 15;
    const speeds = [0.5, 0.75, 1, -0.5, -0.75, -1]; // Adjusted speeds for JS requestAnimationFrame

    currentMinigameState = {
        bar_pos: 0, // Percentage
        bar_speed: speeds[Math.floor(Math.random() * speeds.length)],
        target_zone_start: targetZonePercentageStart,
        target_zone_end: targetZonePercentageStart + (MINIGAME_TARGET_ZONE_WIDTH / MINIGAME_BAR_WIDTH * 100),
        status: 'active', // 'active', 'finished'
        result: null, // 'win', 'loss'
        bar_display_x: barStartX,
        bar_display_y: 300,
    };
}

function updatePlayerMatchMinigame(actionPressed) {
    if (currentMinigameState && currentMinigameState.status === 'active') {
        currentMinigameState.bar_pos += currentMinigameState.bar_speed;

        // Bounce bar
        if (currentMinigameState.bar_pos > 100) {
            currentMinigameState.bar_pos = 100;
            currentMinigameState.bar_speed *= -1;
        } else if (currentMinigameState.bar_pos < 0) {
            currentMinigameState.bar_pos = 0;
            currentMinigameState.bar_speed *= -1;
        }

        if (actionPressed) {
            sounds.minigameAction.play();
            if (currentMinigameState.target_zone_start <= currentMinigameState.bar_pos && currentMinigameState.bar_pos <= currentMinigameState.target_zone_end) {
                currentMinigameState.result = 'win';
                sounds.minigameWin.play();
            } else {
                currentMinigameState.result = 'loss';
                sounds.minigameLoss.play();
            }
            currentMinigameState.status = 'finished';

            // Update match winner based on minigame result
            if (currentMatchInfo) {
                if (currentMinigameState.result === 'win') {
                    currentMatchInfo.winner = currentMatchInfo.player_team;
                } else {
                    currentMatchInfo.winner = currentMatchInfo.opponent_team;
                }
                currentMatchInfo.status = 'finished';
            }
        }
    }
}


// --- Drawing Functions ---

function drawCupTeamSelectionScreen() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'black';
    ctx.font = '60px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText("Escolha seu Time para a Copa", canvas.width / 2, 50);

    ctx.font = '28px sans-serif';
    ctx.fillText("Cima/Baixo para navegar, Enter para selecionar", canvas.width / 2, 100);

    const startY = 150;
    const lineHeight = 40;

    const { selectedTeamIndex, teamsPerPage } = cupTeamSelection;
    let { scrollOffset } = cupTeamSelection;

    if (selectedTeamIndex < scrollOffset) {
        scrollOffset = selectedTeamIndex;
    }
    if (selectedTeamIndex >= scrollOffset + teamsPerPage) {
        scrollOffset = selectedTeamIndex - teamsPerPage + 1;
    }
    cupTeamSelection.scrollOffset = scrollOffset;

    const visibleTeams = TEAMS_DATA.slice(scrollOffset, scrollOffset + teamsPerPage);

    visibleTeams.forEach((team, i) => {
        const actualIndex = scrollOffset + i;
        const displayName = `${actualIndex + 1}. ${team.name}`;

        ctx.font = '36px sans-serif';
        ctx.textAlign = 'left';

        if (actualIndex === selectedTeamIndex) {
            ctx.fillStyle = 'yellow';
            ctx.fillRect(canvas.width / 4 - 10, startY + i * lineHeight, canvas.width / 2 + 20, lineHeight);
            ctx.fillStyle = 'black';
        } else {
            ctx.fillStyle = team.color;
        }

        ctx.fillText(displayName, canvas.width / 4, startY + i * lineHeight + 30);
    });

    const selectedTeam = TEAMS_DATA[cupTeamSelection.selectedTeamIndex];
    if(selectedTeam) {
        const skinImage = penguinSkins[selectedTeam.skin_id];
        if (skinImage && skinImage.complete) {
            ctx.drawImage(skinImage, canvas.width * 0.75 - 75, startY + 50, 150, 150);
        }
    }
}

function drawTournamentBracket() {
    if (!currentCupData) return;

    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const stages = Object.keys(currentCupData.stages);
    const stageWidth = canvas.width / stages.length;

    stages.forEach((stageName, stageIndex) => {
        const matches = currentCupData.stages[stageName];
        const matchHeight = canvas.height / (matches.length + 1);

        ctx.fillStyle = 'black';
        ctx.font = '20px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(stageName, stageIndex * stageWidth + stageWidth / 2, 30);

        matches.forEach((match, matchIndex) => {
            const y = (matchIndex + 1) * matchHeight;
            const x = stageIndex * stageWidth + stageWidth / 2;

            ctx.font = '14px sans-serif';
            const team1Name = match.team1 ? match.team1.name : "TBD";
            const team2Name = match.team2 ? match.team2.name : "TBD";

            let team1Color = match.team1 ? match.team1.color : 'grey';
            let team2Color = match.team2 ? match.team2.color : 'grey';

            if (match.winner) {
                if (match.winner.id === (match.team1 && match.team1.id)) {
                    team2Color = 'lightgrey';
                } else {
                    team1Color = 'lightgrey';
                }
            }

            ctx.fillStyle = team1Color;
            ctx.fillText(team1Name, x, y - 10);
            ctx.fillStyle = 'black';
            ctx.fillText("vs", x, y + 5);
            ctx.fillStyle = team2Color;
            ctx.fillText(team2Name, x, y + 20);

            const skin1 = match.team1 ? penguinSkins[match.team1.skin_id] : null;
            const skin2 = match.team2 ? penguinSkins[match.team2.skin_id] : null;

            if (skin1 && skin1.complete) {
                ctx.drawImage(skin1, x - 100, y - 25, 30, 30);
            }
            if (skin2 && skin2.complete) {
                ctx.drawImage(skin2, x - 100, y + 5, 30, 30);
            }
        });
    });

    if (currentCupData.status === 'finished' && currentCupData.cup_winner) {
        ctx.fillStyle = 'gold';
        ctx.font = '40px sans-serif';
        ctx.fillText(`Campeão da Copa: ${currentCupData.cup_winner.name}!`, canvas.width / 2, canvas.height - 30);
    } else {
        ctx.fillStyle = 'black';
        ctx.font = '20px sans-serif';
        ctx.fillText("Simulando jogos...", canvas.width / 2, canvas.height - 20);
    }
}

function drawCupFinishedScreen() {
    drawTournamentBracket(); // Show the final bracket
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'white';
    ctx.font = '40px sans-serif';
    ctx.textAlign = 'center';
    if(currentCupData && currentCupData.cup_winner) {
        ctx.fillText(`Campeão: ${currentCupData.cup_winner.name}!`, canvas.width / 2, canvas.height / 2 - 50);
    }
    ctx.font = '30px sans-serif';
    ctx.fillText("Pressione Enter para voltar ao Menu.", canvas.width / 2, canvas.height / 2 + 50);
}

function drawPlayerMatchMinigame() {
    if (!currentMinigameState || !currentMatchInfo) return;

    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw team names
    ctx.font = '30px sans-serif';
    ctx.textAlign = 'center';

    const playerTeam = currentMatchInfo.player_team;
    const opponentTeam = currentMatchInfo.opponent_team;

    ctx.fillStyle = playerTeam.color;
    ctx.fillText(`Player: ${playerTeam.name}`, canvas.width * 0.25, 50);

    ctx.fillStyle = opponentTeam.color;
    ctx.fillText(`Opponent: ${opponentTeam.name}`, canvas.width * 0.75, 50);

    if (currentMinigameState.status === 'active') {
        // Draw the background bar
        ctx.fillStyle = 'rgb(100, 100, 100)';
        ctx.fillRect(currentMinigameState.bar_display_x, currentMinigameState.bar_display_y, MINIGAME_BAR_WIDTH, MINIGAME_BAR_HEIGHT);

        // Draw the target zone
        const targetXPos = currentMinigameState.bar_display_x + (currentMinigameState.target_zone_start / 100 * MINIGAME_BAR_WIDTH);
        const targetRectWidth = (currentMinigameState.target_zone_end - currentMinigameState.target_zone_start) / 100 * MINIGAME_BAR_WIDTH;
        ctx.fillStyle = 'rgb(0, 200, 0)';
        ctx.fillRect(targetXPos, currentMinigameState.bar_display_y, targetRectWidth, MINIGAME_BAR_HEIGHT);

        // Draw the moving indicator
        const indicatorXPos = currentMinigameState.bar_display_x + (currentMinigameState.bar_pos / 100 * MINIGAME_BAR_WIDTH);
        const indicatorWidth = 5;
        ctx.fillStyle = 'rgb(255, 0, 0)';
        ctx.fillRect(indicatorXPos - indicatorWidth / 2, currentMinigameState.bar_display_y, indicatorWidth, MINIGAME_BAR_HEIGHT);

        ctx.fillStyle = 'black';
        ctx.font = '24px sans-serif';
        ctx.fillText("Pressione ESPAÇO na zona alvo!", canvas.width / 2, currentMinigameState.bar_display_y + MINIGAME_BAR_HEIGHT + 40);
    } else if (currentMinigameState.status === 'finished') {
        const resultText = currentMinigameState.result === 'win' ? "Você Ganhou!" : "Você Perdeu!";
        ctx.fillStyle = currentMinigameState.result === 'win' ? 'green' : 'red';
        ctx.font = '48px sans-serif';
        ctx.fillText(resultText, canvas.width / 2, canvas.height / 2);

        ctx.fillStyle = 'black';
        ctx.font = '24px sans-serif';
        ctx.fillText("Pressione Enter para continuar.", canvas.width / 2, canvas.height / 2 + 50);
    }
}

// --- Main Menu ---
const mainMenu = {
    options: ["Jogo Rápido", "Copa", "Sair"],
    selectedOption: 0
};

function drawMainMenu() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'black';
    ctx.font = '74px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText("Penguin Battle", canvas.width / 2, 100);

    const menuStartY = 200;
    const optionSpacing = 60;

    mainMenu.options.forEach((option, index) => {
        ctx.font = '50px sans-serif';
        ctx.fillStyle = (index === mainMenu.selectedOption) ? 'yellow' : 'black';
        ctx.fillText(option, canvas.width / 2, menuStartY + index * optionSpacing);
    });
}

// --- Input Handling ---
window.addEventListener('keydown', function(e) {
    if (gameState === 'main_menu') {
        if (e.key === 'ArrowUp') {
            mainMenu.selectedOption = (mainMenu.selectedOption - 1 + mainMenu.options.length) % mainMenu.options.length;
            sounds.menuNavigate.play();
        } else if (e.key === 'ArrowDown') {
            mainMenu.selectedOption = (mainMenu.selectedOption + 1) % mainMenu.options.length;
            sounds.menuNavigate.play();
        } else if (e.key === 'Enter') {
            sounds.menuSelect.play();
            const selectedAction = mainMenu.options[mainMenu.selectedOption];
            if (selectedAction === 'Jogo Rápido') {
                startQuickGame();
            } else if (selectedAction === 'Copa') {
                gameState = 'cup_team_selection';
            } else if (selectedAction === 'Sair') {
                alert("Para sair, feche a aba do navegador.");
            }
        }
    } else if (gameState === 'cup_team_selection') {
        if (e.key === 'ArrowUp') {
            cupTeamSelection.selectedTeamIndex = (cupTeamSelection.selectedTeamIndex - 1 + TEAMS_DATA.length) % TEAMS_DATA.length;
            sounds.menuNavigate.play();
        } else if (e.key === 'ArrowDown') {
            cupTeamSelection.selectedTeamIndex = (cupTeamSelection.selectedTeamIndex + 1) % TEAMS_DATA.length;
            sounds.menuNavigate.play();
        } else if (e.key === 'Enter') {
            sounds.menuSelect.play();
            const selectedTeamId = TEAMS_DATA[cupTeamSelection.selectedTeamIndex].id;
            initializeCup(selectedTeamId);
        }
    } else if (gameState === 'quick_game_active' && currentMinigameState) {
        if (e.key === ' ' && currentMinigameState.status === 'active') { // Space bar
            updatePlayerMatchMinigame(true);
        } else if (e.key === 'Enter' && currentMinigameState.status === 'finished') {
            gameState = 'main_menu';
            currentMatchInfo = null;
            currentMinigameState = null;
        }
    } else if (gameState === 'cup_player_match' && currentMinigameState) {
        if (e.key === ' ' && currentMinigameState.status === 'active') {
            updatePlayerMatchMinigame(true);
        } else if (e.key === 'Enter' && currentMinigameState.status === 'finished') {
            if (activePlayerCupMatch) {
                activePlayerCupMatch.winner = currentMinigameState.result === 'win' ? currentCupData.player_team : currentMatchInfo.opponent_team;
                activePlayerCupMatch.played = true;
            }
            gameState = 'cup_active';
            currentMinigameState = null;
            currentMatchInfo = null;
            activePlayerCupMatch = null;
            advanceCupStage();
        }
    } else if (gameState === 'cup_finished') {
        if (e.key === 'Enter') {
            currentCupData = null;
            gameState = 'main_menu';
        }
    }
});

// Main game loop
function gameLoop() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update game state
    updatePlayerMatchMinigame(false); // Pass false for actionPressed, handled by event listener

    // Update and draw based on game state
    switch (gameState) {
        case 'main_menu':
            drawMainMenu();
            break;
        case 'quick_game_active':
            drawPlayerMatchMinigame();
            break;
        case 'cup_team_selection':
            drawCupTeamSelectionScreen();
            break;
        case 'cup_active':
            drawTournamentBracket();
            break;
        case 'cup_player_match':
            drawPlayerMatchMinigame();
            break;
        case 'cup_finished':
            drawCupFinishedScreen();
            break;
    }

    // Request the next frame
    requestAnimationFrame(gameLoop);
}

// Start the game loop
loadSkins();
gameLoop();
