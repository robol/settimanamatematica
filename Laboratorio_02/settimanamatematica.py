import numpy as np, requests, os
import subprocess
from scipy.io import wavfile
from matplotlib import pyplot as plt
from IPython.display import Audio

plt.style.use('fivethirtyeight')

def sound(v):
  v = v / np.max(np.abs(v))
  wavfile.write("output.wav", 44100, (2**13 * v).astype(np.int16))
  return Audio("output.wav")

def unisci(*args):
  return np.concatenate(args)

"""NOTA2FREQ Determina la frequenza di una nota

 F = NOTA2FREQ(NOMENOTA);
 
 Le note vanno espresse secondo la seguente notazione:

   Do4 -> Do centrale
   Do5 -> Do all'ottava sopra
   
 Altri esempi: Sol#2, Mib3, Fa##4 (:= Sol4) ...

 Il codice non è case sensitive, i.e., 'Sol2', 'sol2, 'SOL2' rappresentano
 tutti la stessa nota.
"""
def nota2freq(nota):
  freq = np.log2(220) + 1 / 4;

  # Separiamo il nome della nota da diesis e ottave
  octave = 0
  leggendo_nome_nota = True;
  nome_nota = "";
  sharps = 0; flats = 0; # Numero di diesis o bemolle

  for j in range(len(nota)):
    if leggendo_nome_nota:
      if ord(nota[j]) < 65 or ord(nota[j]) > 122:
        leggendo_nome_nota = False
        nome_nota = nota[0 : j]
    
    if not leggendo_nome_nota:
      if nota[j] == '#':
        sharps = sharps + 1;
      elif nota[j] == 'b':
        flats = flats + 1;
      else:
        octave = int(nota[j:]) - 4

  # Aggiustiamo la frequenza con l'ottava
  freq = freq + octave

  # Aggiungiamo eventuali diesis o bemolle
  freq = freq + (sharps - flats) / 12.0;

  # E infine regoliamo la frequenza in base alla posizione nella scala
  nome_nota = nome_nota.lower()
  if nome_nota == 'do':
    pass
  elif nome_nota == 're':
    freq = freq + 2 / 12;
  elif nome_nota == 'mi':
    freq = freq + 4 / 12;
  elif nome_nota == 'fa':
    freq = freq + 5 / 12;
  elif nome_nota == 'sol':
    freq = freq + 7 / 12;
  elif nome_nota == 'la':
    freq = freq + 9 / 12;
  elif nome_nota == 'si':
    freq = freq + 11 / 12;
  else:
    raise RuntimeException('Nome nota non supportato')
    
  # Calcoliamo 2^freq
  freq = np.power(2, freq)

  return freq

def download_file(name):
  a = requests.get('http://people.cs.dm.unipi.it/robol/matematica-musica/%s' % name)
  with open(name, 'wb') as h:
    h.write(a.content)

def download_sounds():
  download_file('flute_A4.wav')
  download_file('great-organ_A3.wav')
  download_file('strings_A3.wav')

def analizza_suono(nomefile, freq_base = None):
  if isinstance(nomefile, str):
    Fs, s = wavfile.read(nomefile);
    # Per suoni stereo, selezionamo solo uno dei canali. 
    if s.ndim > 1:
      s = s[:,0]
  else:
    s = nomefile;
    Fs = 44100;

  # Facciamo una copia del suono per intero che ci servirà più tardi, mentre
  # s verrà tagliato a solo una parte iniziale per meglio identificare le
  # frequenze. 
  s_intero = s;

  # Teniamo solo la parte iniziale del suono -- questo ci permette di
  # ignorare il fatto che durante un suono lungo i coefficienti di Fourier
  # cambiano un po'. 
  s = s[8192 : 16384];

  # Calcoliamo la trasformata di Fourier discreta dei sample. Questa è una 
  # trasformata fatta utilizzando i numeri complessi, e restituisce dei 
  # valori da cui si possono ricavare i coefficienti a_i, b_i della serie
  # di Fourier come li abbiamo introdotti noi.
  sf = np.fft.fft(s);
  sf = sf / np.max(np.abs(sf));

  # Leggiamo le frequenze prendendo la prima metà del suono (ovvero estraiamo
  # gli a_i). 
  l = int(np.ceil((len(sf) + 1) / 2));
  freqs = np.abs(sf[0:l]);

  x = ( np.array(range(0, l)) / l * Fs / 2);

  fig = plt.figure(figsize = [ 15, 7 ])
  plt.subplot(1, 2, 1);

  ind = np.array(range(int(np.floor(Fs * 0.1)), int(np.floor(Fs * 0.12))));
  plt.plot(ind / Fs, s_intero[ind]);
  plt.xlabel('t');
  plt.ylabel('s(t)');
  plt.title('Forma d\'onda');

  # set(gcf, 'position', [ 400 400 1400 700 ]);
  ax = plt.subplot(1, 2, 2);
  plt.semilogy(x, freqs);

  # Zoomiamo nel range interessante, dove ci sono le frequenze
  # ragionevolmente udibili per noi. 
  plt.axis([ 0, 4000, 0.5 * np.min(freqs), 1.1 * np.max(freqs) ]);

  plt.title('Coefficienti di Fourier');
  plt.xlabel('Frequenza (Hz)');
  plt.ylabel('Coefficiente di Fourier');

  # TODO: Identifichiamo la frequenze massime
  if freq_base is not None:
    ntones = int(4000 / freq_base)
    c = np.zeros(ntones)
    for j in range(1, ntones+1):
      jj = freq_base * l * 2.0 * j / Fs
      j1 = int(jj * 0.97)
      j2 = int(jj * 1.03)
      c[j-1] = np.max(freqs[j1 : j2])
      if c[j-1] < 1e-2:
        c[j-1] = 0.0

    plt.scatter(1 + freq_base * np.arange(1,ntones+1), c, color='red')

    return c

download_sounds()

# Il codice qui sotto implementa quello che è richiesto per registrare audio 
# dal browser

from IPython.display import Javascript
from base64 import b64decode
from io import BytesIO
from pydub import AudioSegment

RECORD = """
const sleep  = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})

var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async ()=>{
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

from ipywebrtc import AudioRecorder, CameraStream
from IPython.display import Audio

def registra():
    camera = CameraStream(constraints={'audio': True,'video':False})
    recorder = AudioRecorder(stream=camera)
    return recorder

def salva_registrazione(recorder):
    with open('recording.webm', 'wb') as f:
        f.write(recorder.audio.value)
    p = subprocess.call([ 'ffmpeg', '-i', 'recording.webm', '-ac', '1', '-f', 'wav', 'file.wav', '-y', '-hide_banner', '-loglevel', 'panic' ])
    
def audioread(nomefile):
    Fs, s = wavfile.read(nomefile)
    
    if s.ndim > 1:
        s = s[:,0]
    
    return s

