"""WebRTC(AEC).

WebRTC APM Banco de dados de:
1. ReproduçãodeÁudioArquivo(para)
2. Entrada(e)
3. AppWebRTCProcessando
4. OriginaleProcessando  de，

:
    python webrtc_aec_demo.py [ÁudioArquivoCaminho]

:
    python webrtc_aec_demo.py .wav
"""

import ctypes
import os
import sys
import threading
import time
import wave
from ctypes import POINTER, Structure, byref, c_bool, c_float, c_int, c_short, c_void_p

import numpy as np
import pyaudio
import pygame
import soundfile as sf
from pygame import mixer

# DLLArquivodeCaminho
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dll_path = os.path.join(
    project_root, "libs", "webrtc_apm", "win", "x86_64", "libwebrtc_apm.dll"
)

# DLL
try:
    apm_lib = ctypes.CDLL(dll_path)
    print(f"SucessoWebRTC APMBanco de dados: {dll_path}")
except Exception as e:
    print(f"WebRTC APM Banco de dados Falha: {e}")
    sys.exit(1)


# eTipo
class DownmixMethod(ctypes.c_int):
    AverageChannels = 0
    UseFirstChannel = 1


class NoiseSuppressionLevel(ctypes.c_int):
    Low = 0
    Moderate = 1
    High = 2
    VeryHigh = 3


class GainControllerMode(ctypes.c_int):
    AdaptiveAnalog = 0
    AdaptiveDigital = 1
    FixedDigital = 2


class ClippingPredictorMode(ctypes.c_int):
    ClippingEventPrediction = 0
    AdaptiveStepClippingPeakPrediction = 1
    FixedStepClippingPeakPrediction = 2


# Pipeline
class Pipeline(Structure):
    _fields_ = [
        ("MaximumInternalProcessingRate", c_int),
        ("MultiChannelRender", c_bool),
        ("MultiChannelCapture", c_bool),
        ("CaptureDownmixMethod", c_int),
    ]


# PreAmplifier
class PreAmplifier(Structure):
    _fields_ = [("Enabled", c_bool), ("FixedGainFactor", c_float)]


# AnalogMicGainEmulation
class AnalogMicGainEmulation(Structure):
    _fields_ = [("Enabled", c_bool), ("InitialLevel", c_int)]


# CaptureLevelAdjustment
class CaptureLevelAdjustment(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("PreGainFactor", c_float),
        ("PostGainFactor", c_float),
        ("MicGainEmulation", AnalogMicGainEmulation),
    ]


# HighPassFilter
class HighPassFilter(Structure):
    _fields_ = [("Enabled", c_bool), ("ApplyInFullBand", c_bool)]


# EchoCanceller
class EchoCanceller(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("MobileMode", c_bool),
        ("ExportLinearAecOutput", c_bool),
        ("EnforceHighPassFiltering", c_bool),
    ]


# NoiseSuppression
class NoiseSuppression(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("NoiseLevel", c_int),
        ("AnalyzeLinearAecOutputWhenAvailable", c_bool),
    ]


# TransientSuppression
class TransientSuppression(Structure):
    _fields_ = [("Enabled", c_bool)]


# ClippingPredictor
class ClippingPredictor(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("PredictorMode", c_int),
        ("WindowLength", c_int),
        ("ReferenceWindowLength", c_int),
        ("ReferenceWindowDelay", c_int),
        ("ClippingThreshold", c_float),
        ("CrestFactorMargin", c_float),
        ("UsePredictedStep", c_bool),
    ]


# AnalogGainController
class AnalogGainController(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("StartupMinVolume", c_int),
        ("ClippedLevelMin", c_int),
        ("EnableDigitalAdaptive", c_bool),
        ("ClippedLevelStep", c_int),
        ("ClippedRatioThreshold", c_float),
        ("ClippedWaitFrames", c_int),
        ("Predictor", ClippingPredictor),
    ]


# GainController1
class GainController1(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("ControllerMode", c_int),
        ("TargetLevelDbfs", c_int),
        ("CompressionGainDb", c_int),
        ("EnableLimiter", c_bool),
        ("AnalogController", AnalogGainController),
    ]


# InputVolumeController
class InputVolumeController(Structure):
    _fields_ = [("Enabled", c_bool)]


# AdaptiveDigital
class AdaptiveDigital(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("HeadroomDb", c_float),
        ("MaxGainDb", c_float),
        ("InitialGainDb", c_float),
        ("MaxGainChangeDbPerSecond", c_float),
        ("MaxOutputNoiseLevelDbfs", c_float),
    ]


# FixedDigital
class FixedDigital(Structure):
    _fields_ = [("GainDb", c_float)]


# GainController2
class GainController2(Structure):
    _fields_ = [
        ("Enabled", c_bool),
        ("VolumeController", InputVolumeController),
        ("AdaptiveController", AdaptiveDigital),
        ("FixedController", FixedDigital),
    ]


# deConfig
class Config(Structure):
    _fields_ = [
        ("PipelineConfig", Pipeline),
        ("PreAmp", PreAmplifier),
        ("LevelAdjustment", CaptureLevelAdjustment),
        ("HighPass", HighPassFilter),
        ("Echo", EchoCanceller),
        ("NoiseSuppress", NoiseSuppression),
        ("TransientSuppress", TransientSuppression),
        ("GainControl1", GainController1),
        ("GainControl2", GainController2),
    ]


# DLL
apm_lib.WebRTC_APM_Create.restype = c_void_p
apm_lib.WebRTC_APM_Create.argtypes = []

apm_lib.WebRTC_APM_Destroy.restype = None
apm_lib.WebRTC_APM_Destroy.argtypes = [c_void_p]

apm_lib.WebRTC_APM_CreateStreamConfig.restype = c_void_p
apm_lib.WebRTC_APM_CreateStreamConfig.argtypes = [c_int, c_int]

apm_lib.WebRTC_APM_DestroyStreamConfig.restype = None
apm_lib.WebRTC_APM_DestroyStreamConfig.argtypes = [c_void_p]

apm_lib.WebRTC_APM_ApplyConfig.restype = c_int
apm_lib.WebRTC_APM_ApplyConfig.argtypes = [c_void_p, POINTER(Config)]

apm_lib.WebRTC_APM_ProcessReverseStream.restype = c_int
apm_lib.WebRTC_APM_ProcessReverseStream.argtypes = [
    c_void_p,
    POINTER(c_short),
    c_void_p,
    c_void_p,
    POINTER(c_short),
]

apm_lib.WebRTC_APM_ProcessStream.restype = c_int
apm_lib.WebRTC_APM_ProcessStream.argtypes = [
    c_void_p,
    POINTER(c_short),
    c_void_p,
    c_void_p,
    POINTER(c_short),
]

apm_lib.WebRTC_APM_SetStreamDelayMs.restype = None
apm_lib.WebRTC_APM_SetStreamDelayMs.argtypes = [c_void_p, c_int]


def create_apm_config():
    """WebRTC APMConfiguração - Conversãopara，Erro-11"""
    config = Config()

    # ConfigurandoPipeline - UsandoTaxa de amostragem
    config.PipelineConfig.MaximumInternalProcessingRate = 16000  # WebRTCConversãoFrequência
    config.PipelineConfig.MultiChannelRender = False
    config.PipelineConfig.MultiChannelCapture = False
    config.PipelineConfig.CaptureDownmixMethod = DownmixMethod.AverageChannels

    # ConfigurandoPreAmplifier - 
    config.PreAmp.Enabled = False  # Fechando，
    config.PreAmp.FixedGainFactor = 1.0  # Não

    # ConfigurandoLevelAdjustment - Conversão
    config.LevelAdjustment.Enabled = False  # Processando
    config.LevelAdjustment.PreGainFactor = 1.0
    config.LevelAdjustment.PostGainFactor = 1.0
    config.LevelAdjustment.MicGainEmulation.Enabled = False
    config.LevelAdjustment.MicGainEmulation.InitialLevel = 100  # e

    # ConfigurandoHighPassFilter - Usando
    config.HighPass.Enabled = True  # Dispositivo
    config.HighPass.ApplyInFullBand = True  # EmApp，de

    # ConfigurandoEchoCanceller - Conversão
    config.Echo.Enabled = True  # 
    config.Echo.MobileMode = False  # UsandoModoModo
    config.Echo.ExportLinearAecOutput = False
    config.Echo.EnforceHighPassFiltering = True  # Forçar，

    # ConfigurandoNoiseSuppression - EmAguardar
    config.NoiseSuppress.Enabled = True
    config.NoiseSuppress.NoiseLevel = NoiseSuppressionLevel.Moderate  # EmAguardar
    config.NoiseSuppress.AnalyzeLinearAecOutputWhenAvailable = True

    # ConfigurandoTransientSuppression
    config.TransientSuppress.Enabled = False  # Fechando，

    # ConfigurandoGainController1 - 
    config.GainControl1.Enabled = True  # 
    config.GainControl1.ControllerMode = GainControllerMode.AdaptiveDigital
    config.GainControl1.TargetLevelDbfs = 3  # Alvo(de)
    config.GainControl1.CompressionGainDb = 9  # Emde
    config.GainControl1.EnableLimiter = True  # Limitado aDispositivo

    # AnalogGainController
    config.GainControl1.AnalogController.Enabled = False  # Fechando
    config.GainControl1.AnalogController.StartupMinVolume = 0
    config.GainControl1.AnalogController.ClippedLevelMin = 70
    config.GainControl1.AnalogController.EnableDigitalAdaptive = False
    config.GainControl1.AnalogController.ClippedLevelStep = 15
    config.GainControl1.AnalogController.ClippedRatioThreshold = 0.1
    config.GainControl1.AnalogController.ClippedWaitFrames = 300

    # ClippingPredictor
    predictor = config.GainControl1.AnalogController.Predictor
    predictor.Enabled = False
    predictor.PredictorMode = ClippingPredictorMode.ClippingEventPrediction
    predictor.WindowLength = 5
    predictor.ReferenceWindowLength = 5
    predictor.ReferenceWindowDelay = 5
    predictor.ClippingThreshold = -1.0
    predictor.CrestFactorMargin = 3.0
    predictor.UsePredictedStep = True

    # ConfigurandoGainController2 - 
    config.GainControl2.Enabled = False
    config.GainControl2.VolumeController.Enabled = False
    config.GainControl2.AdaptiveController.Enabled = False
    config.GainControl2.AdaptiveController.HeadroomDb = 5.0
    config.GainControl2.AdaptiveController.MaxGainDb = 30.0
    config.GainControl2.AdaptiveController.InitialGainDb = 15.0
    config.GainControl2.AdaptiveController.MaxGainChangeDbPerSecond = 6.0
    config.GainControl2.AdaptiveController.MaxOutputNoiseLevelDbfs = -50.0
    config.GainControl2.FixedController.GainDb = 0.0

    return config


# Áudio（DispositivoSaída）
reference_buffer = []
reference_lock = threading.Lock()


def record_playback_audio(chunk_size, sample_rate, channels):
    """
    DispositivoSaídadeÁudio（de）
    """
    global reference_buffer

    # ：de，Windows  PyAudioIncapaz deDispositivoSaída
    # AppEm，UsandoCapturandoÁudioSaída
    try:
        p = pyaudio.PyAudio()

        # TentativadeSaídaDispositivode（Suportado）
        # ：EmNão，para
        loopback_stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size,
            input_device_index=None,  # TentativaUsandoSaídaDispositivo  paraEntradaFonte
        )

        # Começar
        while True:
            try:
                data = loopback_stream.read(chunk_size, exception_on_overflow=False)
                with reference_lock:
                    reference_buffer.append(data)
            except OSError:
                break

            # Tamanho
            with reference_lock:
                if len(reference_buffer) > 100:  # 2Segundosde
                    reference_buffer = reference_buffer[-100:]
    except Exception as e:
        print(f"Incapaz deÁudio: {e}")
    finally:
        try:
            if "loopback_stream" in locals() and loopback_stream:
                loopback_stream.stop_stream()
                loopback_stream.close()
            if "p" in locals() and p:
                p.terminate()
        except Exception:
            pass


def aec_demo(audio_file):
    """
    WebRTC.
    """
    # PesquisarÁudioArquivoExiste
    if not os.path.exists(audio_file):
        print(f"Erro: NãoparaÁudioArquivo {audio_file}")
        return

    # ÁudioParâmetroConfigurando - UsandoWebRTCConversãodeÁudioParâmetro
    SAMPLE_RATE = 16000  # Taxa de amostragem16kHz (WebRTC AECConversãoTaxa de amostragem)
    CHANNELS = 1  # Canais
    CHUNK = 160  # Quadros(10ms @ 16kHz，WebRTCdeQuadrosTamanho)
    FORMAT = pyaudio.paInt16  # 16BitsPCMFormato

    # InicializandoPyAudio
    p = pyaudio.PyAudio()

    # deÁudioDispositivoInformação
    print("\nÁudioDispositivo:")
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        print(f"Dispositivo {i}: {dev_info['name']}")
        print(f"  - Entrada: {dev_info['maxInputChannels']}")
        print(f"  - Saída: {dev_info['maxOutputChannels']}")
        print(f"  - Taxa de amostragem: {dev_info['defaultSampleRate']}")
    print("")

    # AbrindoEntrada
    input_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    # InicializandopygameReproduçãoÁudio
    pygame.init()
    mixer.init(frequency=SAMPLE_RATE, size=-16, channels=CHANNELS, buffer=CHUNK * 4)

    # ÁudioArquivo
    print(f"ÁudioArquivo: {audio_file}")

    # ÁudioArquivoTaxa de amostragem/
    # ：UsandosoundfileBanco de dadosÁudioArquivo  SuportadoFormato
    try:
        print("Áudio...")
        # UsandosoundfileBanco de dadosOriginalÁudio
        ref_audio_data, orig_sr = sf.read(audio_file, dtype="int16")
        print(
            f"OriginalÁudio: Taxa de amostragem={orig_sr}, ="
            f"{ref_audio_data.shape[1] if len(ref_audio_data.shape) > 1 else 1}"
        )

        # para  Canais(Se)
        if len(ref_audio_data.shape) > 1 and ref_audio_data.shape[1] > 1:
            ref_audio_data = ref_audio_data.mean(axis=1).astype(np.int16)

        # Taxa de amostragem(Se)
        if orig_sr != SAMPLE_RATE:
            print(f"Áudiode{orig_sr}Hzpara{SAMPLE_RATE}Hz...")
            # Usandolibrosaouscipy
            from scipy import signal

            ref_audio_data = signal.resample(
                ref_audio_data, int(len(ref_audio_data) * SAMPLE_RATE / orig_sr)
            ).astype(np.int16)

        # parawavArquivo  pygameReprodução
        temp_wav_path = os.path.join(current_dir, "temp_reference.wav")
        with wave.open(temp_wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2Bytes(16Bits)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(ref_audio_data.tobytes())

        # ÁudioCHUNKTamanhodeQuadros
        ref_audio_frames = []
        for i in range(0, len(ref_audio_data), CHUNK):
            if i + CHUNK <= len(ref_audio_data):
                ref_audio_frames.append(ref_audio_data[i : i + CHUNK])
            else:
                # QuadrosNão  CHUNKTamanho，
                last_frame = np.zeros(CHUNK, dtype=np.int16)
                last_frame[: len(ref_audio_data) - i] = ref_audio_data[i:]
                ref_audio_frames.append(last_frame)

        print(f"ÁudioConcluído，{len(ref_audio_frames)}Quadros")

        # Processando  deWAVArquivo
        mixer.music.load(temp_wav_path)
    except Exception as e:
        print(f"Áudio: {e}")
        sys.exit(1)

    # WebRTC APM
    apm = apm_lib.WebRTC_APM_Create()

    # AppAPM
    config = create_apm_config()
    result = apm_lib.WebRTC_APM_ApplyConfig(apm, byref(config))
    if result != 0:
        print(f"Aviso: APMAppFalha，Erro: {result}")

    # 
    stream_config = apm_lib.WebRTC_APM_CreateStreamConfig(SAMPLE_RATE, CHANNELS)

    # ConfigurandodeTempoCorrespondênciae
    apm_lib.WebRTC_APM_SetStreamDelayMs(apm, 50)

    # 
    original_frames = []
    processed_frames = []
    reference_frames = []

    # AguardandoÁudio
    time.sleep(0.5)

    print("ComeçareProcessando...")
    print("ReproduçãoÁudio...")

    mixer.music.play()

    # Tempo(ÁudioArquivoComprimento)
    try:
        sound_length = mixer.Sound(temp_wav_path).get_length()
        recording_time = sound_length if sound_length > 0 else 10
    except Exception:
        recording_time = 10  # SeIncapaz deComprimento，10Segundos

    recording_time += 1  # 1SegundosCapturandoÁudio

    start_time = time.time()
    current_ref_frame_index = 0
    try:
        while time.time() - start_time < recording_time:
            # deQuadrosDados
            input_data = input_stream.read(CHUNK, exception_on_overflow=False)

            # Original
            original_frames.append(input_data)

            # EntradaDadosparashort
            input_array = np.frombuffer(input_data, dtype=np.int16)
            input_ptr = input_array.ctypes.data_as(POINTER(c_short))

            # ÁudioQuadros
            if current_ref_frame_index < len(ref_audio_frames):
                ref_array = ref_audio_frames[current_ref_frame_index]
                reference_frames.append(ref_array.tobytes())
                current_ref_frame_index += 1
            else:
                # SeÁudioReprodução，UsandoQuadros
                ref_array = np.zeros(CHUNK, dtype=np.int16)
                reference_frames.append(ref_array.tobytes())

            ref_ptr = ref_array.ctypes.data_as(POINTER(c_short))

            # Saída
            output_array = np.zeros(CHUNK, dtype=np.int16)
            output_ptr = output_array.ctypes.data_as(POINTER(c_short))

            # ：Processando（DispositivoSaída）
            # deSaída（NãoUsando）
            ref_output_array = np.zeros(CHUNK, dtype=np.int16)
            ref_output_ptr = ref_output_array.ctypes.data_as(POINTER(c_short))

            result_reverse = apm_lib.WebRTC_APM_ProcessReverseStream(
                apm, ref_ptr, stream_config, stream_config, ref_output_ptr
            )

            if result_reverse != 0:
                print(f"\rAviso: ProcessandoFalha，Erro: {result_reverse}")

            # Processando，App
            result = apm_lib.WebRTC_APM_ProcessStream(
                apm, input_ptr, stream_config, stream_config, output_ptr
            )

            if result != 0:
                print(f"\rAviso: ProcessandoFalha，Erro: {result}")

            # Processando  deÁudioQuadros
            processed_frames.append(output_array.tobytes())

            # 
            progress = (time.time() - start_time) / recording_time * 100
            sys.stdout.write(f"\rProcessando: {progress:.1f}%")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nEm")
    finally:
        print("\neProcessandoConcluído")

        # PararReprodução
        mixer.music.stop()

        # FechandoÁudio
        input_stream.stop_stream()
        input_stream.close()

        # APM  Fonte
        apm_lib.WebRTC_APM_DestroyStreamConfig(stream_config)
        apm_lib.WebRTC_APM_Destroy(apm)

        # FechandoPyAudio
        p.terminate()

        # Original
        original_output_path = os.path.join(current_dir, "original_recording.wav")
        save_wav(original_output_path, original_frames, SAMPLE_RATE, CHANNELS)

        # Processando  de
        processed_output_path = os.path.join(current_dir, "processed_recording.wav")
        save_wav(processed_output_path, processed_frames, SAMPLE_RATE, CHANNELS)

        # Áudio（ReproduçãodeÁudio）
        reference_output_path = os.path.join(current_dir, "reference_playback.wav")
        save_wav(reference_output_path, reference_frames, SAMPLE_RATE, CHANNELS)

        # DeletandoArquivo
        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception:
                pass

        print(f"OriginalJá: {original_output_path}")
        print(f"Processando  deJá: {processed_output_path}")
        print(f"ÁudioJá: {reference_output_path}")

        # pygame
        pygame.quit()


def save_wav(file_path, frames, sample_rate, channels):
    """
    ÁudioQuadrosparaWAVArquivo.
    """
    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2Bytes(16Bits)
        wf.setframerate(sample_rate)
        if isinstance(frames[0], bytes):
            wf.writeframes(b"".join(frames))
        else:
            wf.writeframes(b"".join([f for f in frames if isinstance(f, bytes)]))


if __name__ == "__main__":
    # Comando  Parâmetro
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        # UsandoscriptsDiretório  de.wav
        audio_file = os.path.join(current_dir, ".wav")

        # SeArquivoNãoExiste，TentativaMP3Versão
        if not os.path.exists(audio_file):
            audio_file = os.path.join(current_dir, ".mp3")
            if not os.path.exists(audio_file):
                print("Erro: NãoparaÁudioArquivo，ReproduçãodeÁudioArquivoCaminho")
                print(": python webrtc_aec_demo.py [ÁudioArquivoCaminho]")
                sys.exit(1)

    # 
    aec_demo(audio_file)
