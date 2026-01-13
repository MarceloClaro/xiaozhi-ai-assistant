#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import sounddevice as sd


def detect_audio_devices():
    """
    ÁudioDispositivo (Usandosounddevice)
    """
    print("\n===== ÁudioDispositivo (SoundDevice) =====\n")

    # Dispositivo
    default_input = sd.default.device[0] if sd.default.device else None
    default_output = sd.default.device[1] if sd.default.device else None

    # EncontradodeDispositivo
    input_devices = []
    output_devices = []

    # Dispositivo
    devices = sd.query_devices()
    for i, dev_info in enumerate(devices):
        # DispositivoInformação
        print(f"Dispositivo {i}: {dev_info['name']}")
        print(f"  - Entrada: {dev_info['max_input_channels']}")
        print(f"  - Saída: {dev_info['max_output_channels']}")
        print(f"  - Taxa de amostragem: {dev_info['default_samplerate']}")

        # Dispositivo
        if i == default_input:
            print("  - 🎤 EntradaDispositivo")
        if i == default_output:
            print("  - 🔊 SaídaDispositivo")

        # IdentificandoEntradaDispositivo（）
        if dev_info["max_input_channels"] > 0:
            input_devices.append((i, dev_info["name"]))
            if "USB" in dev_info["name"]:
                print("  - USB 🎤")

        # IdentificandoSaídaDispositivo（Dispositivo）
        if dev_info["max_output_channels"] > 0:
            output_devices.append((i, dev_info["name"]))
            if "Headphones" in dev_info["name"]:
                print("  - Saída 🎧")
            elif "USB" in dev_info["name"] and dev_info["max_output_channels"] > 0:
                print("  - USBDispositivo 🔊")

        print("")

    # EncontradodeDispositivo
    print("\n===== Dispositivo =====\n")

    print("EncontradodeEntradaDispositivo（）:")
    for idx, name in input_devices:
        default_mark = " ()" if idx == default_input else ""
        print(f"  - Dispositivo {idx}: {name}{default_mark}")

    print("\nEncontradodeSaídaDispositivo（Dispositivo）:")
    for idx, name in output_devices:
        default_mark = " ()" if idx == default_output else ""
        print(f"  - Dispositivo {idx}: {name}{default_mark}")

    # Dispositivo
    print("\nDispositivo:")

    # 
    recommended_mic = None
    if default_input is not None:
        recommended_mic = (default_input, devices[default_input]["name"])
    elif input_devices:
        # USBDispositivo
        for idx, name in input_devices:
            if "USB" in name:
                recommended_mic = (idx, name)
                break
        if recommended_mic is None:
            recommended_mic = input_devices[0]

    # Dispositivo
    recommended_speaker = None
    if default_output is not None:
        recommended_speaker = (default_output, devices[default_output]["name"])
    elif output_devices:
        # 
        for idx, name in output_devices:
            if "Headphones" in name:
                recommended_speaker = (idx, name)
                break
        if recommended_speaker is None:
            recommended_speaker = output_devices[0]

    if recommended_mic:
        print(f"  - : Dispositivo {recommended_mic[0]} ({recommended_mic[1]})")
    else:
        print("  - NãoEncontrado")

    if recommended_speaker:
        print(f"  - Dispositivo: Dispositivo {recommended_speaker[0]} ({recommended_speaker[1]})")
    else:
        print("  - NãoEncontradoDispositivo")

    print("\n===== SoundDevice =====\n")

    if recommended_mic:
        print("# Inicializando")
        print(f"input_device_id = {recommended_mic[0]}  # {recommended_mic[1]}")
        print("input_stream = sd.InputStream(")
        print("    samplerate=16000,")
        print("    channels=1,")
        print("    dtype=np.int16,")
        print("    blocksize=1024,")
        print(f"    device={recommended_mic[0]},")
        print("    callback=input_callback)")

    if recommended_speaker:
        print("\n# DispositivoInicializando")
        print(
            f"output_device_id = {recommended_speaker[0]}  # "
            f"{recommended_speaker[1]}"
        )
        print("output_stream = sd.OutputStream(")
        print("    samplerate=44100,")
        print("    channels=1,")
        print("    dtype=np.int16,")
        print("    blocksize=1024,")
        print(f"    device={recommended_speaker[0]},")
        print("    callback=output_callback)")

    print("\n===== Dispositivo =====\n")

    # Dispositivo
    if recommended_mic:
        print(f"Em (Dispositivo {recommended_mic[0]})...")
        try:
            sd.rec(
                int(1 * 16000),
                samplerate=16000,
                channels=1,
                device=recommended_mic[0],
                dtype=np.int16,
            )
            sd.wait()
            print("✓ Sucesso")
        except Exception as e:
            print(f"✗ Falha: {e}")

    if recommended_speaker:
        print(f"EmDispositivo (Dispositivo {recommended_speaker[0]})...")
        try:
            # Áudio (440Hz)
            duration = 0.5
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            test_audio = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.int16)

            sd.play(test_audio, samplerate=sample_rate, device=recommended_speaker[0])
            sd.wait()
            print("✓ DispositivoSucesso")
        except Exception as e:
            print(f"✗ DispositivoFalha: {e}")

    return recommended_mic, recommended_speaker


if __name__ == "__main__":
    try:
        mic, speaker = detect_audio_devices()
        print("\nConcluído！")
    except Exception as e:
        print(f"Em: {e}")
