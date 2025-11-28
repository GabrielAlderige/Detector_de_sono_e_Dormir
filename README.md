📘 Detector de Sono e Bocejo em Tempo Real
Usando OpenCV, MediaPipe, EAR/MAR e Sistema Inteligente de Alertas

Este projeto realiza detecção de sonolência e bocejos em tempo real utilizando:

OpenCV → captura de vídeo e exibição

MediaPipe Face Mesh → rastreamento dos olhos e boca

EAR (Eye Aspect Ratio) → cálculo do fechamento dos olhos

MAR (Mouth Aspect Ratio) → detecção de bocejo

Sistema de agregação inteligente (janela de 60s)

Alertas imediatos de risco (som, logs e chamadas opcionais)

🔔 O projeto emite sons sempre que detecta:

Bocejos repetitivos

Sonolência leve → olhos frequentemente fechados

Situação crítica → olhos fechados por muito tempo

📦 Tecnologias Usadas

Python 3.11

OpenCV

MediaPipe

EasyOCR (opcional, se usar leitura de placas)

Playsound / Pygame (para alertas)

Deques para análise temporal

JSON para configurações dinâmicas

📁 Estrutura do Projeto
project/
│
├── detector_sono.py
├── utils.py
├── constants.py
│
├── modules/
│ ├── notificacoes.py
│ └── chamadas.py (opcional)
│
├── configs/
│ └── config.json
│
├── alerts/
│ ├── alert_sono.mp3
│ └── alert_bocejo.mp3
│
├── logs/
│
└── README.md

⚙️ Configurações (config.json)

Você pode ajustar os thresholds em:

configs/config.json

Exemplo:

{
"threshold_EAR": 0.22,
"limite_frames": 8,
"threshold_MAR": 0.8,
"limite_bocejo_frames": 12,
"agg_window_seconds": 60,
"bocejos_per_window_threshold": 5,
"total_eye_closed_seconds_threshold": 6,
"eye_continuous_threshold_seconds": 6,
"notification_cooldown_seconds": 300
}

🛠 Como Instalar e Rodar
1️⃣ Clone o repositório
git clone https://github.com/seu-usuario/nome-do-projeto
cd nome-do-projeto

✔ OPÇÃO 1 — Rodar com Ambiente Virtual (RECOMENDADO)
2️⃣ Criar e ativar a venv
Windows:
python -m venv venv
venv\Scripts\activate

Linux/Mac:
python3 -m venv venv
source venv/bin/activate

3️⃣ Instalar dependências
pip install -r requirements.txt

4️⃣ Rodar o detector
python detector_sono.py

✔ OPÇÃO 2 — Rodar sem venv

(permitido, mas não recomendado)

Se todas as libs estiverem instaladas globalmente:

python detector_sono.py

▶️ Como Usar

Abra o script

A webcam será iniciada automaticamente

O sistema processa seu rosto em tempo real

Alertas sonoros tocam em três situações:

🔸 Sonolência leve

Olhos se fechando frequentemente

🔸 Bocejos repetidos

Número de bocejos maior que o limite configurado

🔥 Risco extremo

Olhos fechados por muito tempo (ex.: ≥ 6s)
O sistema toca alerta imediato independentemente dos outros thresholds

📊 Lógica Principal
EAR (Eye Aspect Ratio)

Detecta fechamento dos olhos:

EAR < threshold_EAR → olhos fechados

MAR (Mouth Aspect Ratio)

Detecta bocejo:

MAR > threshold_MAR → bocejo

Agregação Inteligente (janela de 60s)

Bocejos repetidos

Total de olhos fechados

Fechamento contínuo

🔔 Sistema de Alertas

O script usa:

modules/notificacoes.py

Para emitir alertas:

sons

logs em arquivo

notificações de console

E suporta chamadas automáticas (caso instaladas):

modules/chamadas.py

🧪 Tecla para sair

A qualquer momento:

q

Fecha a webcam e encerra o programa.

🧱 Requisitos do Sistema

Webcam funcionando

Python 3.9+

CPU moderna (MediaPipe é leve, sem GPU)
