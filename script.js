// --- DADOS DOS PERSONAGENS ---
const PERSONAGENS = [
    {nome: "Harry Potter", casa: "Gryffindor", papel: "O protagonista", foto: "imagens/harry.png"},
    {nome: "Hermione Granger", casa: "Gryffindor", papel: "Estudante brilhante", foto: "imagens/hermione.png"},
    {nome: "Ron Weasley", casa: "Gryffindor", papel: "Melhor amigo", foto: "imagens/ron.png"},
    {nome: "Albus Dumbledore", casa: "Gryffindor", papel: "Diretor de Hogwarts", foto: "imagens/dumbledore.png"},
    {nome: "Severus Snape", casa: "Slytherin", papel: "Professor de Poções", foto: "imagens/snape.png"},
    {nome: "Sirius Black", casa: "Gryffindor", papel: "Padrinho do Harry", foto: "imagens/sirius.png"},
    {nome: "Rubeus Hagrid", casa: "Gryffindor", papel: "Guarda-caça", foto: "imagens/hagrid.png"},
    {nome: "Draco Malfoy", casa: "Slytherin", papel: "Rival do Harry", foto: "imagens/draco.png"},
    {nome: "Lord Voldemort", casa: "Slytherin", papel: "Antagonista", foto: "imagens/voldemort.png"},
    {nome: "Neville Longbottom", casa: "Gryffindor", papel: "Herói improvável", foto: "imagens/neville.jpg"},
    {nome: "Luna Lovegood", casa: "Ravenclaw", papel: "Estudante excêntrica", foto: "imagens/luna.png"},
    {nome: "Ginny Weasley", casa: "Gryffindor", papel: "Irmã do Ron", foto: "imagens/ginny.png"},
    {nome: "Minerva McGonagall", casa: "Gryffindor", papel: "Professora de Transfiguração", foto: "imagens/minerva.png"},
    {nome: "Remus Lupin", casa: "Gryffindor", papel: "Professor e lobisomem", foto: "imagens/lupin.jpg"},
    {nome: "Bellatrix Lestrange", casa: "Slytherin", papel: "Comensal da Morte", foto: "imagens/bellatrix.png"},
    {nome: "Dobby", casa: "Nenhuma", papel: "Elfo Doméstico", foto: "imagens/dobby.png"}
];

// --- VARIÁVEIS DE ESTADO ---
let currentLives = 0;
let targetChar = {};
let availableHints = [];
let gameActive = false;
let currentScore = 0;

// --- FUNÇÕES DE ÁUDIO ---
function playSound(id) {
    const audio = document.getElementById(id);
    if(audio) {
        audio.currentTime = 0;
        audio.play().catch(e => console.log("Áudio bloqueado:", e));
    }
}

// --- UTILITÁRIOS ---
function normalize(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function log(message, type="neutral") {
    const logDiv = document.querySelector('.parchment-log');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    if(type === 'error') entry.style.color = '#8b0000';
    if(type === 'success') entry.style.color = '#006400';
    if(type === 'hint') entry.style.color = '#00008b';

    entry.innerHTML = message;
    logDiv.appendChild(entry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

// --- JOGO ---

function startGame() {
    playSound('somAbertura');

    // Configuração
    const diffSelect = document.getElementById('difficulty');
    currentLives = parseInt(diffSelect.value);
    targetChar = PERSONAGENS[Math.floor(Math.random() * PERSONAGENS.length)];
    
    const hints = [
        `Casa: ${targetChar.casa}`,
        `Papel: ${targetChar.papel}`,
        `Primeira Letra: ${targetChar.nome[0]}`,
        `Total de Letras: ${targetChar.nome.replace(' ', '').length}`
    ];
    availableHints = hints.sort(() => Math.random() - 0.5);

    // Reset UI
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('game-screen').classList.add('active');
    
    document.getElementById('end-buttons').style.display = 'none';
    document.getElementById('input-area').style.display = 'block';
    document.getElementById('result-area').style.display = 'none';
    document.getElementById('guess-input').value = '';
    document.getElementById('game-title').textContent = "Quem é o Bruxo?";
    document.querySelector('.parchment-log').innerHTML = '';
    
    document.getElementById('guess-input').disabled = false;
    document.querySelector('.btn-guess').disabled = false;
    document.querySelector('.btn-hint').disabled = false;

    gameActive = true;
    currentScore = 0; // Reinicia pontuação da partida atual
    updateHUD();
    log("📜 O Cálice de fogo escolheu um nome...", "neutral");
}

function updateHUD() {
    const livesDisplay = document.getElementById('lives-display');
    let bolts = "⚡".repeat(currentLives);
    livesDisplay.innerText = `Vidas: ${bolts} (${currentLives})`;
    livesDisplay.style.color = currentLives <= 2 ? "red" : "var(--gold)";
    
    document.getElementById('score-display').innerText = `Pontos Atuais: ${calculateScore()}`;
}

function calculateScore() {
    // 100 pontos base + 50 por vida restante
    return 100 + (currentLives * 50);
}

function getHint() {
    if (!gameActive) return;

    if (currentLives <= 1) {
        alert("Sua magia está muito fraca! Se usar uma dica agora, você perde o jogo.");
    }

    if (availableHints.length === 0) {
        log("⚠️ Não há mais dicas no livro!");
        return;
    }

    playSound('somMagia');
    currentLives--;
    const hint = availableHints.shift();
    log(`🧪 DICA: ${hint}`, "hint");
    updateHUD();
    checkGameOver();
}

function checkGuess() {
    if (!gameActive) return;

    const input = document.getElementById('guess-input');
    const guess = input.value;
    
    if (!guess) return;

    if (guess.toLowerCase() === 'revelio') {
        getHint();
        input.value = '';
        return;
    }

    const normGuess = normalize(guess);
    const normTarget = normalize(targetChar.nome);

    if (normGuess === normTarget || (normGuess.length > 3 && normTarget.includes(normGuess))) {
        gameWin();
    } else {
        playSound('somErro');
        currentLives--;
        log(`❌ '${guess}' está incorreto.`, "error");
        
        input.classList.add('shake');
        setTimeout(() => input.classList.remove('shake'), 500);
        
        input.value = '';
        updateHUD();
        checkGameOver();
    }
}

function checkGameOver() {
    if (currentLives <= 0) {
        gameActive = false;
        playSound('somErro');
        showResult(false);
    }
}

function gameWin() {
    gameActive = false;
    playSound('somAcerto');
    currentScore = calculateScore(); // Consolida a pontuação final
    showResult(true);
    
    // Pergunta o nome e salva
    setTimeout(() => {
        const playerName = prompt("✨ ACERTOU! Digite seu nome para o Ranking:", "Bruxo Anônimo");
        if(playerName) {
            saveScore(playerName, currentScore);
        }
    }, 500);
}

function showResult(isWin) {
    document.getElementById('input-area').style.display = 'none';
    document.getElementById('end-buttons').style.display = 'flex';

    const resultArea = document.getElementById('result-area');
    const charPhoto = document.getElementById('char-photo');
    const resultText = document.getElementById('result-text');

    charPhoto.src = targetChar.foto;
    resultArea.style.display = 'flex';

    if (isWin) {
        document.getElementById('game-title').textContent = "✨ Vitória! ✨";
        resultText.innerHTML = `Acertou! É <b>${targetChar.nome}</b><br>Pontuação: ${currentScore}`;
        resultText.style.color = "#00ff00";
        log(`<br>✨ ACERTOU! <b>${targetChar.nome}</b>`, "success");
    } else {
        document.getElementById('game-title').textContent = "💀 Fim de Jogo";
        resultText.innerHTML = `O bruxo era <b>${targetChar.nome}</b>`;
        resultText.style.color = "red";
        log(`<br>💀 Suas vidas acabaram.`, "error");
    }
}

function resetGame() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('start-screen').classList.add('active');
}

// --- RANKING SYSTEM ---

function saveScore(name, score) {
    // Pega o ranking atual do localStorage (ou cria array vazio)
    let ranking = JSON.parse(localStorage.getItem('harryPotterRanking')) || [];
    
    // Adiciona novo recorde
    ranking.push({
        name: name,
        score: score,
        date: new Date().toLocaleDateString()
    });

    // Ordena do maior para o menor
    ranking.sort((a, b) => b.score - a.score);

    // Mantém apenas os top 10
    ranking = ranking.slice(0, 10);

    // Salva de volta
    localStorage.setItem('harryPotterRanking', JSON.stringify(ranking));
}

function showRankingScreen() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('ranking-screen').classList.add('active');
    
    const list = document.getElementById('ranking-list');
    list.innerHTML = '';
    
    const ranking = JSON.parse(localStorage.getItem('harryPotterRanking')) || [];

    if (ranking.length === 0) {
        list.innerHTML = '<li>Nenhum bruxo registrado ainda.</li>';
        return;
    }

    ranking.forEach((entry, index) => {
        const li = document.createElement('li');
        // Adiciona medalhas para os top 3
        let medal = '';
        if (index === 0) medal = '🥇 ';
        if (index === 1) medal = '🥈 ';
        if (index === 2) medal = '🥉 ';

        li.innerHTML = `
            <span>${medal}${index + 1}. ${entry.name} <small>(${entry.date})</small></span>
            <span class="score">${entry.score} pts</span>
        `;
        list.appendChild(li);
    });
}

function backToMenu() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('start-screen').classList.add('active');
}

document.getElementById('guess-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') checkGuess();
});