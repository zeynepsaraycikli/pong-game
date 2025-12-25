import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import pygame

# Başlat ses sistemi
pygame.mixer.init()
hitSound = pygame.mixer.Sound("Resources/hit.wav")

# Fonksiyon: Alpha kanalı ekle
def ensure_alpha_channel(image):
    if image.shape[2] == 3:
        b, g, r = cv2.split(image)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255
        image = cv2.merge([b, g, r, alpha])
    return image

# Görselleri yükle
imgBackground = cv2.imread("Resources/Background.png")
imgGameOver = cv2.imread("Resources/gameOver.png")
imgBall = ensure_alpha_channel(cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED))
imgBat1 = ensure_alpha_channel(cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED))
imgBat2 = ensure_alpha_channel(cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED))

# Kamera ayarları
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# El algılayıcı
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Başlangıç değişkenleri
ballPos = [100, 100]
score = [0, 0]
roundCount = 0
gameOver = False
speedX, speedY = 0, 0

# Kullanıcıdan isimleri ve zorluk seçimini alma
leftPlayer = input("Sol Oyuncu Adı: ")
rightPlayer = input("Sağ Oyuncu Adı: ")
print("Zorluk Seçin: 1 - Kolay | 2 - Orta | 3 - Zor")
difficulty = int(input("Seçiminiz (1/2/3): "))

# Zorluk seviyesine göre hız ayarla
if difficulty == 1:
    baseSpeed = 10
elif difficulty == 2:
    baseSpeed = 15
else:
    baseSpeed = 20

speedX, speedY = baseSpeed, baseSpeed

# Ana oyun döngüsü
while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    hands, img = detector.findHands(img, flipType=False)
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    if not gameOver:
        if hands:
            for hand in hands:
                x, y, w, h = hand['bbox']
                h1, w1, _ = imgBat1.shape
                y1 = y - h1 // 2
                y1 = np.clip(y1, 20, 415)

                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                    if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX * 1.05
                        speedY = speedY * 1.05
                        ballPos[0] += 30
                        hitSound.play()

                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                    if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX * 1.05
                        speedY = speedY * 1.05
                        ballPos[0] -= 30
                        hitSound.play()

        # Gol olursa skor ver
        if ballPos[0] < 40:
            score[1] += 1
            roundCount += 1
            ballPos = [640, 360]
            speedX = baseSpeed
            speedY = baseSpeed

        elif ballPos[0] > 1200:
            score[0] += 1
            roundCount += 1
            ballPos = [640, 360]
            speedX = -baseSpeed
            speedY = baseSpeed

        # Duvara çarparsa zıplat
        if ballPos[1] >= 500 or ballPos[1] <= 10:
            speedY = -speedY

        ballPos[0] += int(speedX)
        ballPos[1] += int(speedY)

        # Topu ekle
        img = cvzone.overlayPNG(img, imgBall, (int(ballPos[0]), int(ballPos[1])))

        # Skorları yazdır
        cv2.putText(img, f"{leftPlayer}: {score[0]}", (100, 50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f"{rightPlayer}: {score[1]}", (800, 50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f"Tur: {roundCount}/10", (500, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 0), 3)

        # 10 tur bitti mi kontrol et
        if roundCount >= 10:
            gameOver = True

    else:
        # Game over ekranı üzerine yazı yaz
        img = imgGameOver.copy()
        if score[0] > score[1]:
            resultText = f"{leftPlayer} WINS!"
        elif score[1] > score[0]:
            resultText = f"{rightPlayer} WINS!"
        else:
            resultText = "NO WINNER !"

        cv2.putText(img, resultText, (400, 300), cv2.FONT_HERSHEY_COMPLEX, 2, (200, 0, 200), 5)
        cv2.putText(img, f"Skor: {score[0]} - {score[1]}", (500, 380), cv2.FONT_HERSHEY_COMPLEX, 1.5, (200, 0, 200), 4)
        cv2.putText(img, "R - RESTART | Q - QUIT", (420, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Kamera önizleme küçük pencere
    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    cv2.imshow("Pong Game", img)
    key = cv2.waitKey(1)

    # Tekrar başlat
    if key == ord('r') and gameOver:
        ballPos = [100, 100]
        score = [0, 0]
        roundCount = 0
        speedX, speedY = baseSpeed, baseSpeed
        gameOver = False

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
