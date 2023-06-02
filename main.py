import io
import os
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from textblob import TextBlob

#Sesden gelen yazıları bu text değişkenine ekleyeceğiz
text = ""
import os
from pydub import AudioSegment

def split_audio(audio_file, chunk_duration):
    # Ses dosyasını yükle
    audio = AudioSegment.from_file(audio_file)

    # Toplam süreyi hesapla
    total_duration = len(audio)

    # Boş bir liste oluştur
    chunks = []

    # Başlangıç ve bitiş zamanlarını ayarla
    start_time = 0
    end_time = chunk_duration * 1000

    # Parçaları belirli sürelerle bölmek için döngüyü kullan
    while end_time <= total_duration:
        # Belirli süre aralığında bir parça al ve listeye ekle
        chunk = audio[start_time:end_time]
        chunks.append(chunk)

        # Başlangıç ve bitiş zamanlarını güncelle
        start_time = end_time
        end_time += chunk_duration * 1000

    # Son parçayı ekle (başlangıç zamanı, toplam süreden küçükse)
    if start_time < total_duration:
        chunk = audio[start_time:total_duration]
        chunks.append(chunk)

    # Parçalardan oluşan liste döndür
    return chunks

def transcribe_file(speech_file):
    global text
    client = speech.SpeechClient()
    
    # Tek kanallı (mono) olarak dönüştür
    audio = AudioSegment.from_file(speech_file).set_channels(1)
    
    # BytesIO kullanarak audio içeriğini bir bellek akışına dönüştür
    with io.BytesIO() as audio_stream:
        audio.export(audio_stream, format='wav')
        audio_content = audio_stream.getvalue()

    # Recognize API'si için tanımlanan audio nesnesini oluştur
    audio = speech.RecognitionAudio(content=audio_content)

    # RecognitionConfig oluştur ve ayarları belirle
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code='en-US')

    # Ses dosyasını transkribe etmek için istemciye talepte bulun
    response = client.recognize(config=config, audio=audio)

    # Transkriptleri al ve yazdır
    for result in response.results:
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))

        # Transkripti toplam metin değişkenine ekle
        text += result.alternatives[0].transcript
        # print(text)

#Google anahtarını ekle
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

#Sesi uygun parçalara böl (Google limitleri yüzünden)
audio_chunks = split_audio('voice1.wav', 40 )

def sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Olumsuz"
    else:
        return "Notr"
print("Sesler çeviriliyor..")
#Her bir ses parçasını yazıya dönüştür
for i, chunk in enumerate(audio_chunks):
    chunk.export(f'chunk{i+1}.wav', format='wav')
    transcribe_file(f'chunk{i+1}.wav')
    os.remove(f'chunk{i+1}.wav')
print("------------------")
print("TEXT")
print(text)
print("------------------")
print(f"Result: {sentiment_analysis(text)}")




