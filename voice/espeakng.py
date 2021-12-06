from espeakng import ESpeakNG
import wave
import StringIO

esng = ESpeakNG()
esng.say('Hello World!')

esng.voice = 'english-us'
esng.say("[[h@l'oU w'3:ld]]")


wavs = esng.synth_wav('Hello World!')
wav = wave.open(StringIO.StringIO(wavs))
print wav.getnchannels(), wav.getframerate(), wav.getnframes()