# detector_sono.py (versão revisada, otimizada e com correções)
import time
import json
import cv2
import mediapipe as mp
from collections import deque

from utils import calcular_EAR, calcular_MAR
from constants import olho_direito, olho_esquerdo, boca_pontos
from modules.notificacoes import tocar_alerta, log_evento

# Módulo opcional de chamadas
try:
    from modules.chamadas import fazer_ligacao
except Exception:
    def fazer_ligacao(numero): 
        pass

# ==========================
# CARREGAR CONFIGURAÇÕES
# ==========================
try:
    with open("configs/config.json") as f:
        config = json.load(f)
except Exception as e:
    print("\nERRO ao carregar config.json — carregando valores padrão!")
    print(e)
    config = {}

# thresholds básicos
threshold_EAR = config.get("threshold_EAR", 0.22)
limite_frames = config.get("limite_frames", 8)
threshold_MAR = config.get("threshold_MAR", 0.8)
limite_bocejo_frames = config.get("limite_bocejo_frames", 12)
alerta_sono = config.get("alerta_sono", "alerts/alert_sono.mp3")
alerta_bocejo = config.get("alerta_bocejo", "alerts/alert_bocejo.mp3")

# parâmetros de agregação
AGG_WINDOW = config.get("agg_window_seconds", 60)
BOCEJOS_THRESHOLD = config.get("bocejos_per_window_threshold", 5)
TOTAL_EYE_CLOSED_SECONDS_THRESHOLD = config.get("total_eye_closed_seconds_threshold", 6)
EYE_CONTINUOUS_THRESHOLD = config.get("eye_continuous_threshold_seconds", 6)
NOTIF_COOLDOWN = config.get("notification_cooldown_seconds", 300)
MIN_EYE_CLOSURE_RECORD = config.get("min_eye_closure_record_seconds", 0.3)

# ==========================
# VARIÁVEIS INTERNAS
# ==========================
bocejo_times = deque()
eye_closures = []

eye_closed_start = None
last_notification_time = 0
last_agg_check = time.time()

contador_sono = 0
contador_bocejo = 0

# ==========================
# MEDIA PIPE
# ==========================
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("❌ ERRO: Nenhuma câmera detectada.")

# ==========================
# FUNÇÕES AUXILIARES
# ==========================
def limpar_historico_antigo(now):
    """Limpa dados antigos para evitar estouro de memória."""
    limite = AGG_WINDOW * 3

    while bocejo_times and now - bocejo_times[0] > limite:
        bocejo_times.popleft()

    while eye_closures and now - eye_closures[0][0] > limite:
        eye_closures.pop(0)


def contar_bocejos_janela(now):
    return sum(1 for t in bocejo_times if now - t <= AGG_WINDOW)


def soma_olhos_fechados_janela(now):
    total = 0
    for end, dur in eye_closures:
        if now - end <= AGG_WINDOW:
            total += dur
    return total


def existe_closure_continuo(now):
    for end, dur in eye_closures:
        if now - end <= AGG_WINDOW and dur >= EYE_CONTINUOUS_THRESHOLD:
            return True
    return False


def notificar(tipo, msg, arquivo_som):
    """Envia notificação com cooldown automático."""
    global last_notification_time
    now = time.time()

    if now - last_notification_time < NOTIF_COOLDOWN:
        return

    log_evento(tipo, msg)
    tocar_alerta(arquivo_som)
    last_notification_time = now


def avaliar_aggregados():
    now = time.time()
    limpar_historico_antigo(now)

    bocejos = contar_bocejos_janela(now)
    total_eye = soma_olhos_fechados_janela(now)
    long_closure = existe_closure_continuo(now)

    print(f"[AGG] bocejos={bocejos}, olhos_fechados={total_eye:.2f}s, closure_longo={long_closure}")

    # Regras de risco
    if bocejos >= BOCEJOS_THRESHOLD:
        notificar("AGG_ALERTA", f"Muitos bocejos: {bocejos} em {AGG_WINDOW}s", alerta_bocejo)
        return

    if total_eye >= TOTAL_EYE_CLOSED_SECONDS_THRESHOLD:
        notificar("AGG_ALERTA", f"Olhos fechados por {total_eye:.1f}s em {AGG_WINDOW}s", alerta_sono)
        return

    if long_closure:
        notificar("AGG_ALERTA", f"Fechamento longo detectado ({EYE_CONTINUOUS_THRESHOLD}s)", alerta_sono)
        return

# ==========================
# LOOP PRINCIPAL
# ==========================
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar câmera.")
            break

        altura, largura = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        now = time.time()

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:

                # Desenhar malha facial
                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS
                )

                # ======= OLHOS =======
                olhoR = [(int(face_landmarks.landmark[i].x * largura),
                          int(face_landmarks.landmark[i].y * altura)) for i in olho_direito]

                olhoL = [(int(face_landmarks.landmark[i].x * largura),
                          int(face_landmarks.landmark[i].y * altura)) for i in olho_esquerdo]

                EAR = (calcular_EAR(olhoR) + calcular_EAR(olhoL)) / 2

                if EAR < threshold_EAR:
                    if eye_closed_start is None:
                        eye_closed_start = now
                else:
                    if eye_closed_start is not None:
                        dur = now - eye_closed_start
                        if dur >= MIN_EYE_CLOSURE_RECORD:
                            eye_closures.append((now, dur))
                            log_evento("Olhos fechados", f"{dur:.2f}s")
                        eye_closed_start = None

                # Aviso imediato (risco extremo)
                if eye_closed_start is not None and (now - eye_closed_start) >= EYE_CONTINUOUS_THRESHOLD:
                    notificar("ImmediateAlert", "Olhos fechados por tempo perigoso!", alerta_sono)

                # ======= BOCEJO =======
                boca = [(int(face_landmarks.landmark[i].x * largura),
                         int(face_landmarks.landmark[i].y * altura)) for i in boca_pontos]

                MAR = calcular_MAR(boca)

                if MAR > threshold_MAR:
                    contador_bocejo += 1

                    if contador_bocejo == limite_bocejo_frames:
                        bocejo_times.append(now)
                        log_evento("Bocejo detectado", f"MAR={MAR:.2f}")
                else:
                    contador_bocejo = 0

        # Exibe imagem
        cv2.imshow("Detector de Sono e Bocejo", frame)

        # Avaliação agregada por janela
        if now - last_agg_check >= AGG_WINDOW:
            avaliar_aggregados()
            last_agg_check = now

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Fechar tudo
cap.release()
cv2.destroyAllWindows()
