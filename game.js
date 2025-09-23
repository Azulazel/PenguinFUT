// game.js for Penguinfut 2023
// This file will contain the logic for the more complex penguin soccer game.

// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game constants (from the new Python code)
const TELA_LARGURA = 1200;
const TELA_ALTURA = 800;
const COR_BG = 'rgb(80, 200, 80)';
const VELOCIDADE_PINGUIM = 5;
const VELOCIDADE_BOLA = 12;
const VELOCIDADE_BOT = 3;
const COR_PINGUIM = 'rgb(0, 0, 0)';
const COR_BICO_PES = 'rgb(255, 165, 0)';
const COR_BOLA = 'rgb(255, 255, 255)';
const TAMANHO_GOL = { width: 50, height: 150 };
const COR_TEXTO = 'rgb(255, 255, 255)';
const TEMPO_JOGO = 60;

// Adjust canvas size to match the new constants
canvas.width = TELA_LARGURA;
canvas.height = TELA_ALTURA;

// Game state
let gameState = 'menu'; // 'menu', 'playing', 'game_over'

// Game objects will be defined here
let jogador = new Pinguim(TELA_LARGURA / 4, TELA_ALTURA / 2, COR_PINGUIM);
let bot = new Bot(3 * TELA_LARGURA / 4, TELA_ALTURA / 2, 'red');
let bola = new Bola(TELA_LARGURA / 2, TELA_ALTURA / 2);

// UI and Game State variables
const gol_esquerda_rect = { x: 0, y: (TELA_ALTURA - TAMANHO_GOL.height) / 2, width: TAMANHO_GOL.width, height: TAMANHO_GOL.height };
const gol_direita_rect = { x: TELA_LARGURA - TAMANHO_GOL.width, y: (TELA_ALTURA - TAMANHO_GOL.height) / 2, width: TAMANHO_GOL.width, height: TAMANHO_GOL.height };
let placar_jogador = 0;
let placar_bot = 0;
let inicio_jogo = null;
let gameOverStartTime = null;

function resetPositions() {
    jogador.x = TELA_LARGURA / 4;
    jogador.y = TELA_ALTURA / 2;
    bot.x = 3 * TELA_LARGURA / 4;
    bot.y = TELA_ALTURA / 2;
    bola.x = TELA_LARGURA / 2;
    bola.y = TELA_ALTURA / 2;
    bola.velocity = { x: 0, y: 0 };
}

function reiniciar_jogo() {
    placar_jogador = 0;
    placar_bot = 0;
    resetPositions();
    inicio_jogo = Date.now();
    gameState = 'playing';
    gameOverStartTime = null;
}

// A simple AABB collision check
function checkRectCollision(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}


class Pinguim {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.width = 50;
        this.height = 70;
        this.color = color;
        this.speed = VELOCIDADE_PINGUIM;
    }

    draw(ctx) {
        // Body
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.ellipse(this.x, this.y, this.width / 2, this.height / 2, 0, 0, 2 * Math.PI);
        ctx.fill();

        // Belly
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.ellipse(this.x, this.y + 5, 15, 22.5, 0, 0, 2 * Math.PI);
        ctx.fill();

        // Beak
        ctx.fillStyle = COR_BICO_PES;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y - 20);
        ctx.lineTo(this.x - 5, this.y - 30);
        ctx.lineTo(this.x + 5, this.y - 30);
        ctx.closePath();
        ctx.fill();

        // Eyes
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.ellipse(this.x - 10, this.y - 25, 5, 5, 0, 0, 2 * Math.PI);
        ctx.ellipse(this.x + 10, this.y - 25, 5, 5, 0, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.ellipse(this.x - 8, this.y - 25, 3, 3, 0, 0, 2 * Math.PI);
        ctx.ellipse(this.x + 12, this.y - 25, 3, 3, 0, 0, 2 * Math.PI);
        ctx.fill();

        // Feet
        ctx.fillStyle = COR_BICO_PES;
        ctx.beginPath();
        ctx.ellipse(this.x - 7, this.y + 32, 5, 2.5, 0, 0, 2 * Math.PI);
        ctx.ellipse(this.x + 7, this.y + 32, 5, 2.5, 0, 0, 2 * Math.PI);
        ctx.fill();
    }

    mover(direction) {
        if (direction === 'ESQUERDA' && this.x - this.width / 2 > 0) {
            this.x -= this.speed;
        } else if (direction === 'DIREITA' && this.x + this.width / 2 < TELA_LARGURA) {
            this.x += this.speed;
        } else if (direction === 'CIMA' && this.y - this.height / 2 > 0) {
            this.y -= this.speed;
        } else if (direction === 'BAIXO' && this.y + this.height / 2 < TELA_ALTURA) {
            this.y += this.speed;
        }
    }
}

class Bot extends Pinguim {
    constructor(x, y, color) {
        super(x, y, color);
        this.dashSpeed = 10;
        this.dashDuration = 0.5;
        this.dashStartTime = null;
        this.velocity = { x: 0, y: 0 };
    }

    mover_para_bola(bola) {
        if (this.dashStartTime && Date.now() - this.dashStartTime < this.dashDuration * 1000) {
            return;
        }
        const deltaX = bola.x - this.x;
        const deltaY = bola.y - this.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        if (distance > 0) {
            const dirX = deltaX / distance;
            const dirY = deltaY / distance;
            this.x += dirX * VELOCIDADE_BOT;
            this.y += dirY * VELOCIDADE_BOT;
        }
        this.clamp_ip();
    }

    update() {
        if (this.dashStartTime && Date.now() - this.dashStartTime >= this.dashDuration * 1000) {
            this.velocity = { x: 0, y: 0 };
            this.dashStartTime = null;
        }
        this.x += this.velocity.x;
        this.y += this.velocity.y;
        this.clamp_ip();
    }

    dash(direction) {
        this.velocity.x = direction.x * this.dashSpeed;
        this.velocity.y = direction.y * this.dashSpeed;
        this.dashStartTime = Date.now();
    }

    clamp_ip() {
        this.x = Math.max(this.width / 2, Math.min(this.x, TELA_LARGURA - this.width / 2));
        this.y = Math.max(this.height / 2, Math.min(this.y, TELA_ALTURA - this.height / 2));
    }
}

class Bola {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.radius = 20;
        this.color = COR_BOLA;
        this.velocity = { x: 0, y: 0 };
        this.friction = 0.06;
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        ctx.fill();
    }

    update() {
        this.x += this.velocity.x;
        this.y += this.velocity.y;

        const speed = Math.sqrt(this.velocity.x * this.velocity.x + this.velocity.y * this.velocity.y);
        if (speed > 0) {
            const frictionEffect = {
                x: (this.velocity.x / speed) * this.friction,
                y: (this.velocity.y / speed) * this.friction
            };
            this.velocity.x -= frictionEffect.x;
            this.velocity.y -= frictionEffect.y;

            if (speed < this.friction) {
                this.velocity = { x: 0, y: 0 };
            }
        }

        // Wall collisions
        if (this.x - this.radius < 0) this.velocity.x = Math.abs(this.velocity.x);
        if (this.x + this.radius > TELA_LARGURA) this.velocity.x = -Math.abs(this.velocity.x);
        if (this.y - this.radius < 0) this.velocity.y = Math.abs(this.velocity.y);
        if (this.y + this.radius > TELA_ALTURA) this.velocity.y = -Math.abs(this.velocity.y);
    }

    chutar(pinguim) {
        const deltaX = this.x - pinguim.x;
        const deltaY = this.y - pinguim.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        if (distance === 0) return;
        const dirX = deltaX / distance;
        const dirY = deltaY / distance;
        this.velocity.x = dirX * VELOCIDADE_BOLA;
        this.velocity.y = dirY * VELOCIDADE_BOLA;
    }
}


// Input state
const keys = {};
window.addEventListener('keydown', (e) => {
    keys[e.key] = true;
});
window.addEventListener('keyup', (e) => {
    keys[e.key] = false;
});


// Main game loop
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function update() {
    // Update logic based on gameState
    switch (gameState) {
        case 'menu':
            // Handle menu logic
            if (keys['Enter']) {
                gameState = 'playing';
                inicio_jogo = Date.now(); // Start timer when game begins
            }
            break;
        case 'playing':
            // Timer check
            if (inicio_jogo && (Date.now() - inicio_jogo) / 1000 >= TEMPO_JOGO) {
                gameState = 'game_over';
                gameOverStartTime = Date.now();
            }

            // Player movement
            if (keys['ArrowLeft']) jogador.mover('ESQUERDA');
            if (keys['ArrowRight']) jogador.mover('DIREITA');
            if (keys['ArrowUp']) jogador.mover('CIMA');
            if (keys['ArrowDown']) jogador.mover('BAIXO');

            // Bot movement and update
            bot.mover_para_bola(bola);
            bot.update();

            // Ball update
            bola.update();

            // --- Collision Detection ---
            const jogadorRect = { x: jogador.x - jogador.width/2, y: jogador.y - jogador.height/2, width: jogador.width, height: jogador.height };
            const botRect = { x: bot.x - bot.width/2, y: bot.y - bot.height/2, width: bot.width, height: bot.height };
            const bolaRect = { x: bola.x - bola.radius, y: bola.y - bola.radius, width: bola.radius*2, height: bola.radius*2 };

            // Penguin-ball collision
            if (checkRectCollision(jogadorRect, bolaRect)) bola.chutar(jogador);
            if (checkRectCollision(botRect, bolaRect)) bola.chutar(bot);

            // Goal detection
            if (checkRectCollision(bolaRect, gol_direita_rect)) {
                placar_jogador++;
                resetPositions();
            }
            if (checkRectCollision(bolaRect, gol_esquerda_rect)) {
                placar_bot++;
                resetPositions();
            }

            // Penguin-penguin collision
            if (checkRectCollision(jogadorRect, botRect)) {
                const dx = jogador.x - bot.x;
                const dy = jogador.y - bot.y;
                const distance = Math.sqrt(dx*dx + dy*dy);
                const overlap = (jogador.width/2 + bot.width/2) - distance;
                if(overlap > 0) {
                    const separationX = (dx/distance) * overlap;
                    const separationY = (dy/distance) * overlap;
                    jogador.x += separationX / 2;
                    jogador.y += separationY / 2;
                    bot.x -= separationX / 2;
                    bot.y -= separationY / 2;
                }
            }

            // Player dash kick
            if (keys[' ']) { // space bar
                const dx = bot.x - jogador.x;
                const dy = bot.y - jogador.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if(dist < 80) {
                    const dir = {x: dx/dist, y: dy/dist};
                    bot.dash(dir);
                }
            }

            break;
        case 'game_over':
            // Handle game over logic
            if (gameOverStartTime && Date.now() - gameOverStartTime > 5000) {
                reiniciar_jogo();
            }
            break;
    }
}

function draw() {
    // Drawing logic based on gameState
    ctx.fillStyle = COR_BG;
    ctx.fillRect(0, 0, TELA_LARGURA, TELA_ALTURA);

    switch (gameState) {
        case 'menu':
            // Draw menu
            ctx.fillStyle = COR_TEXTO;
            ctx.font = '74px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Penguinfut 2023', TELA_LARGURA / 2, TELA_ALTURA / 2 - 50);
            ctx.font = '50px sans-serif';
            ctx.fillText('Pressione Enter para iniciar', TELA_LARGURA / 2, TELA_ALTURA / 2 + 50);
            break;
        case 'playing':
            // Draw game elements
            ctx.strokeStyle = COR_TEXTO;
            ctx.lineWidth = 2;
            ctx.strokeRect(gol_esquerda_rect.x, gol_esquerda_rect.y, gol_esquerda_rect.width, gol_esquerda_rect.height);
            ctx.strokeRect(gol_direita_rect.x, gol_direita_rect.y, gol_direita_rect.width, gol_direita_rect.height);

            jogador.draw(ctx);
            bot.draw(ctx);
            bola.draw(ctx);

            // Draw Score and Timer
            ctx.fillStyle = COR_TEXTO;
            ctx.font = '36px sans-serif';
            ctx.textAlign = 'center';
            const placar_texto = `Jogador: ${placar_jogador}  Bot: ${placar_bot}`;
            ctx.fillText(placar_texto, TELA_LARGURA / 2, 30);

            const tempo_decorrido = (Date.now() - inicio_jogo) / 1000;
            const tempo_restante = Math.max(0, TEMPO_JOGO - tempo_decorrido);
            const tempo_texto = `Tempo: ${Math.ceil(tempo_restante)}`;
            ctx.textAlign = 'left';
            ctx.fillText(tempo_texto, 10, 30);

            break;
        case 'game_over':
            // Draw game over screen
            ctx.fillStyle = COR_TEXTO;
            ctx.font = '74px sans-serif';
            ctx.textAlign = 'center';
            const vencedor = placar_jogador > placar_bot ? "Jogador" : placar_bot > placar_jogador ? "Bot" : "Empate";
            ctx.fillText(`Vencedor: ${vencedor}`, TELA_LARGURA / 2, TELA_ALTURA / 2 - 40);
            ctx.font = '50px sans-serif';
            ctx.fillText(`Placar final: ${placar_jogador} - ${placar_bot}`, TELA_LARGURA / 2, TELA_ALTURA / 2 + 40);
            break;
    }
}

// Start the game
gameLoop();
