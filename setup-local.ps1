param(
    [ValidateSet("install", "build", "up", "down", "logs", "restart")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"

# Este script executa apenas tarefas locais.
# 1. Cria o arquivo .env a partir do modelo, se ainda nao existir.
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

# 2. Os passos de ambiente virtual e dependencias sao usados para execucao local sem Docker.
if ($Action -in @("install", "build", "up", "restart")) {
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }

    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r .\services\api\requirements.txt
    python -m pip install -r .\services\payment\requirements.txt
    python -m pip install -r .\services\notification\requirements.txt
}

if ($Action -eq "install") {
    return
}

# 3. Build dos containers para garantir que todos os servicos estejam prontos.
if ($Action -in @("build", "up", "restart")) {
    docker compose build
}

switch ($Action) {
    "build" {
        return
    }
    "up" {
        # 4. Sobe todos os servicos em segundo plano.
        docker compose up -d
    }
    "restart" {
        # 4. Reinicia o ambiente completo de containers.
        docker compose down
        docker compose up -d
    }
    "down" {
        # Comando auxiliar para parar e remover os containers.
        docker compose down
    }
    "logs" {
        # Comando auxiliar para acompanhar os logs de todos os servicos.
        docker compose logs -f
    }
}
