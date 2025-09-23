// game.js for Penguinfut 2023 - v2
// This file will contain the logic for the more complex penguin soccer game,
// with a focus on time-based physics for stability.

// Get the canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game constants
const TELA_LARGURA = 1200;
const TELA_ALTURA = 800;
const COR_BG = 'rgb(80, 200, 80)';
const VELOCIDADE_PINGUIM = 300; // pixels per second
const VELOCIDADE_BOLA = 720;   // pixels per second
const VELOCIDADE_BOT = 180;    // pixels per second
const COR_PINGUIM = 'rgb(0, 0, 0)';
const COR_BICO_PES = 'rgb(255, 165, 0)';
const COR_BOLA = 'rgb(255, 255, 255)';
const TAMANHO_GOL = { width: 50, height: 150 };
const COR_TEXTO = 'rgb(255, 255, 255)';
const TEMPO_JOGO = 60; // seconds

// Adjust canvas size
canvas.width = TELA_LARGURA;
canvas.height = TELA_ALTURA;

// Game state and objects
let gameState = 'menu'; // 'menu', 'playing', 'game_over'
let gameOverStartTime = null;
let jogador = new Pinguim(TELA_LARGURA / 4, TELA_ALTURA / 2, COR_PINGUIM);
let bot = new Bot(3 * TELA_LARGURA / 4, TELA_ALTURA / 2, 'red');
let bola = new Bola(TELA_LARGURA / 2, TELA_ALTURA / 2);

const gol_esquerda_rect = { x: 0, y: (TELA_ALTURA - TAMANHO_GOL.height) / 2, width: TAMANHO_GOL.width, height: TAMANHO_GOL.height };
const gol_direita_rect = { x: TELA_LARGURA - TAMANHO_GOL.width, y: (TELA_ALTURA - TAMANHO_GOL.height) / 2, width: TAMANHO_GOL.width, height: TAMANHO_GOL.height };
let placar_jogador = 0;
let placar_bot = 0;
let inicio_jogo = null;

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

    mover(direction, deltaTime) {
        const moveDistance = this.speed * deltaTime;
        if (direction === 'ESQUERDA' && this.x - this.width / 2 > 0) {
            this.x -= moveDistance;
        } else if (direction === 'DIREITA' && this.x + this.width / 2 < TELA_LARGURA) {
            this.x += moveDistance;
        } else if (direction === 'CIMA' && this.y - this.height / 2 > 0) {
            this.y -= moveDistance;
        } else if (direction === 'BAIXO' && this.y + this.height / 2 < TELA_ALTURA) {
            this.y += moveDistance;
        }
    }
}

class Bot extends Pinguim {
    constructor(x, y, color) {
        super(x, y, color);
        this.dashSpeed = 600;
        this.dashDuration = 0.5;
        this.dashStartTime = null;
        this.velocity = { x: 0, y: 0 };
        this.speed = VELOCIDADE_BOT;
    }

    mover_para_bola(bola, deltaTime) {
        if (this.dashStartTime && performance.now() - this.dashStartTime < this.dashDuration * 1000) {
            return;
        }
        const deltaX = bola.x - this.x;
        const deltaY = bola.y - this.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        if (distance > 0) {
            const dirX = deltaX / distance;
            const dirY = deltaY / distance;
            this.x += dirX * this.speed * deltaTime;
            this.y += dirY * this.speed * deltaTime;
        }
        this.clamp_ip();
    }

    update(deltaTime) {
        if (this.dashStartTime && performance.now() - this.dashStartTime >= this.dashDuration * 1000) {
            this.velocity = { x: 0, y: 0 };
            this.dashStartTime = null;
        }
        this.x += this.velocity.x * deltaTime;
        this.y += this.velocity.y * deltaTime;
        this.clamp_ip();
    }

    dash(direction) {
        this.velocity.x = direction.x * this.dashSpeed;
        this.velocity.y = direction.y * this.dashSpeed;
        this.dashStartTime = performance.now();
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
        this.friction = 0.99; // Multiplicative friction
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        ctx.fill();
    }

    update(deltaTime) {
        this.x += this.velocity.x * deltaTime;
        this.y += this.velocity.y * deltaTime;

        // Apply friction
        this.velocity.x *= this.friction;
        this.velocity.y *= this.friction;

        if (Math.sqrt(this.velocity.x**2 + this.velocity.y**2) < 1) {
            this.velocity = { x: 0, y: 0 };
        }

        // Wall collisions
        const force = 60; // Extra force in pixels/sec
        if (this.x - this.radius < 0) {
            this.velocity.x = Math.abs(this.velocity.x);
            this.velocity.x += force * deltaTime;
        }
        if (this.x + this.radius > TELA_LARGURA) {
            this.velocity.x = -Math.abs(this.velocity.x);
            this.velocity.x -= force * deltaTime;
        }
        if (this.y - this.radius < 0) {
            this.velocity.y = Math.abs(this.velocity.y);
            this.velocity.y += force * deltaTime;
        }
        if (this.y + this.radius > TELA_ALTURA) {
            this.velocity.y = -Math.abs(this.velocity.y);
            this.velocity.y -= force * deltaTime;
        }
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

// let jogador, bot, bola;

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
    inicio_jogo = performance.now();
    gameState = 'playing';
    gameOverStartTime = null;
}

function checkRectCollision(rect1, rect2) {
    // AABB collision detection
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

// Input state
const keys = {};
window.addEventListener('keydown', (e) => { keys[e.key] = true; });
window.addEventListener('keyup', (e) => { keys[e.key] = false; });

// Time-based game loop
let lastTime = 0;
function gameLoop(timestamp) {
    if(!lastTime) lastTime = timestamp;
    const deltaTime = (timestamp - lastTime) / 1000; // delta time in seconds
    lastTime = timestamp;

    update(deltaTime);
    draw();

    requestAnimationFrame(gameLoop);
}

function update(deltaTime) {
    switch (gameState) {
        case 'menu':
            if (keys['Enter']) {
                gameState = 'playing';
                inicio_jogo = performance.now();
            }
            break;
        case 'playing':
            // Check for game over condition
            if (inicio_jogo && (performance.now() - inicio_jogo) / 1000 >= TEMPO_JOGO) {
                gameState = 'game_over';
                gameOverStartTime = performance.now();
            }

            // Handle Player Movement
            if (keys['ArrowLeft']) jogador.mover('ESQUERDA', deltaTime);
            if (keys['ArrowRight']) jogador.mover('DIREITA', deltaTime);
            if (keys['ArrowUp']) jogador.mover('CIMA', deltaTime);
            if (keys['ArrowDown']) jogador.mover('BAIXO', deltaTime);

            // Handle Bot and Ball updates
            bot.mover_para_bola(bola, deltaTime);
            bot.update(deltaTime);
            bola.update(deltaTime);

            // --- Collision and Gameplay Logic ---
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
            } else if (checkRectCollision(bolaRect, gol_esquerda_rect)) {
                placar_bot++;
                resetPositions();
            }

            // Penguin-penguin collision
            if (checkRectCollision(jogadorRect, botRect)) {
                const dx = jogador.x - bot.x;
                const dy = jogador.y - bot.y;
                const distance = Math.sqrt(dx*dx + dy*dy);
                if (distance > 0) {
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
            if (gameOverStartTime && performance.now() - gameOverStartTime > 5000) {
                reiniciar_jogo();
            }
            break;
    }
}

function draw() {
    // Clear canvas
    ctx.fillStyle = COR_BG;
    ctx.fillRect(0, 0, TELA_LARGURA, TELA_ALTURA);

    switch (gameState) {
        case 'menu':
            ctx.fillStyle = COR_TEXTO;
            ctx.font = '74px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Penguinfut 2023', TELA_LARGURA / 2, TELA_ALTURA / 2 - 50);
            ctx.font = '50px sans-serif';
            ctx.fillText('Pressione Enter para iniciar', TELA_LARGURA / 2, TELA_ALTURA / 2 + 50);
            break;
        case 'playing':
            // Draw goals
            ctx.strokeStyle = COR_TEXTO;
            ctx.lineWidth = 2;
            ctx.strokeRect(gol_esquerda_rect.x, gol_esquerda_rect.y, gol_esquerda_rect.width, gol_esquerda_rect.height);
            ctx.strokeRect(gol_direita_rect.x, gol_direita_rect.y, gol_direita_rect.width, gol_direita_rect.height);

            // Draw game objects
            jogador.draw(ctx);
            bot.draw(ctx);
            bola.draw(ctx);

            // Draw UI
            ctx.fillStyle = COR_TEXTO;
            ctx.font = '36px sans-serif';
            ctx.textAlign = 'center';
            const placar_texto = `Jogador: ${placar_jogador}  Bot: ${placar_bot}`;
            ctx.fillText(placar_texto, TELA_LARGURA / 2, 30);

            const tempo_decorrido = (performance.now() - inicio_jogo) / 1000;
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
requestAnimationFrame(gameLoop);
