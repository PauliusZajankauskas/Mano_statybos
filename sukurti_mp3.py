from gtts import gTTS

text = "Užduotis:\nPastatyk bokštą iš šešių kaladėlių.\n Pasirink šias  spalvas:\nraudona, geltona, žalia"
tts = gTTS(text=text, lang='lt')
tts.save("assets/sounds/uzduotis.mp3")

print("✅ Įrašyta į: assets/sounds/uzduotis.mp3")