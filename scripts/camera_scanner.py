#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Arquivo: camera_scanner.py

import json
import logging
import sys
import time
from pathlib import Path

import cv2

# ConfigManager
from src.utils.config_manager import ConfigManager

# DiretórioparaCaminho，srcEmde
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# ConfigurandoLog
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CameraScanner")


def get_camera_capabilities(cam):
    """
    deParâmetroe.
    """
    capabilities = {}

    # de
    standard_resolutions = [
        (640, 480),  # VGA
        (800, 600),  # SVGA
        (1024, 768),  # XGA
        (1280, 720),  # HD
        (1280, 960),  # 4:3 HD
        (1920, 1080),  # Full HD
        (2560, 1440),  # QHD
        (3840, 2160),  # 4K UHD
    ]

    supported_resolutions = []
    original_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Original
    capabilities["default_resolution"] = (original_width, original_height)

    # 
    for width, height in standard_resolutions:
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # SeConfigurandoSucesso（comde）
        if actual_width == width and actual_height == height:
            supported_resolutions.append((width, height))

    # RestaurandoOriginal
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, original_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, original_height)

    capabilities["supported_resolutions"] = supported_resolutions

    # Quadros
    fps = int(cam.get(cv2.CAP_PROP_FPS))
    capabilities["fps"] = fps if fps > 0 else 30  # para30fps

    # Nome
    backend_name = cam.getBackendName()
    capabilities["backend"] = backend_name

    return capabilities


def detect_cameras():
    """
    .
    """
    print("\n===== Dispositivo =====\n")

    # ConfigManager
    config_manager = ConfigManager.get_instance()

    # 
    current_camera_config = config_manager.get_config("CAMERA", {})
    logger.info(f": {current_camera_config}")

    # 
    if current_camera_config:
        print(":")
        print(f"  - : {current_camera_config.get('camera_index', 'NãoConfigurando')}")
        print(
            f"  - : {current_camera_config.get('frame_width', 'NãoConfigurando')}x{current_camera_config.get('frame_height', 'NãoConfigurando')}"
        )
        print(
            f"  - : {current_camera_config.get('frame_width', 'NãoConfigurando')}x{current_camera_config.get('frame_height', 'NãoConfigurando')}"
        )
        print(f"  - Quadros: {current_camera_config.get('fps', 'NãoConfigurando')}")
        print(f"  - VLModelo: {current_camera_config.get('models', 'NãoConfigurando')}")
        print("")

    # EncontradodeDispositivo
    camera_devices = []

    # TentativaAbrindo
    max_cameras_to_check = 10  # Pesquisar10

    for i in range(max_cameras_to_check):
        try:
            # TentativaAbrindo
            cap = cv2.VideoCapture(i)

            if cap.isOpened():
                # Informação
                device_name = f"Camera {i}"
                try:
                    # EmDispositivoNome
                    device_name = cap.getBackendName() + f" Camera {i}"
                except Exception as e:
                    logger.warning(f"Dispositivo{i}NomeFalha: {e}")

                # Quadros
                ret, frame = cap.read()
                if not ret:
                    print(f"Dispositivo {i}: AbrindoSucessoIncapaz de，")
                    cap.release()
                    continue

                # 
                capabilities = get_camera_capabilities(cap)

                # DispositivoInformação
                width, height = capabilities["default_resolution"]
                resolutions_str = ", ".join(
                    [f"{w}x{h}" for w, h in capabilities["supported_resolutions"]]
                )

                print(f"Dispositivo {i}: {device_name}")
                print(f"  - : {width}x{height}")
                print(f"  - Suportado: {resolutions_str}")
                print(f"  - Quadros: {capabilities['fps']}")
                print(f"  - : {capabilities['backend']}")

                # Usandode
                current_index = current_camera_config.get("camera_index")
                if current_index == i:
                    print("Usandode")

                # paraDispositivo
                camera_devices.append(
                    {"index": i, "name": device_name, "capabilities": capabilities}
                )

                # 
                print(f"EmDispositivo {i} de...")
                try:
                    #  - Quadros
                    test_frames = 0
                    start_time = time.time()

                    while test_frames < 10 and time.time() - start_time < 2:
                        ret, frame = cap.read()
                        if ret:
                            test_frames += 1
                        else:
                            break

                    if test_frames >= 5:
                        print(f"  ✓  ( {test_frames} Quadros)")
                    else:
                        print(f"  ⚠ Exceção ( {test_frames} Quadros)")

                except Exception as e:
                    print(f"  ✗ Falha: {e}")

                # 
                print(f"Dispositivo {i} de？(y/n，n): ", end="")
                show_preview = input().strip().lower()

                if show_preview == "y":
                    print(f"EmDispositivo {i} de， 'q' ouAguardando3SegundosContinuar...")
                    preview_start = time.time()

                    while time.time() - preview_start < 3:
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow(f"Camera {i} Preview", frame)
                            if cv2.waitKey(1) & 0xFF == ord("q"):
                                break

                    cv2.destroyAllWindows()

                cap.release()

            else:
                # SeIncapaz deAbrindo，então  paraNenhum
                consecutive_failures = 0
                for j in range(i, i + 2):
                    temp_cap = cv2.VideoCapture(j)
                    if not temp_cap.isOpened():
                        consecutive_failures += 1
                    temp_cap.release()

                if consecutive_failures >= 2 and i > 0:
                    break

        except Exception as e:
            print(f"Dispositivo {i} : {e}")

    # EncontradodeDispositivo
    print("\n===== Dispositivo =====\n")

    if not camera_devices:
        print("NãoEncontradodeDispositivo！")
        return None

    print(f"Encontrado {len(camera_devices)} Dispositivo:")
    for device in camera_devices:
        width, height = device["capabilities"]["default_resolution"]
        print(f"  - Dispositivo {device['index']}: {device['name']}")
        print(f"    : {width}x{height}")

    # Dispositivo
    print("\n===== Dispositivo =====\n")

    # ，Vezesde
    recommended_camera = None
    highest_resolution = 0

    for device in camera_devices:
        width, height = device["capabilities"]["default_resolution"]
        resolution = width * height

        # Se  HDou
        if width >= 1280 and height >= 720:
            if resolution > highest_resolution:
                highest_resolution = resolution
                recommended_camera = device
        elif recommended_camera is None or resolution > highest_resolution:
            highest_resolution = resolution
            recommended_camera = device

    # Dispositivo
    if recommended_camera:
        r_width, r_height = recommended_camera["capabilities"]["default_resolution"]
        print(
            f": Dispositivo {recommended_camera['index']} "
            f"({recommended_camera['name']})"
        )
        print(f"  - : {r_width}x{r_height}")
        print(f"  - Quadros: {recommended_camera['capabilities']['fps']}")

    # deEmVL APIInformação
    vl_url = current_camera_config.get(
        "Loacl_VL_url", "https://open.bigmodel.cn/api/paas/v4/"
    )
    vl_api_key = current_camera_config.get("VLapi_key", "dekey")
    model = current_camera_config.get("models", "glm-4v-plus")

    # Arquivo
    print("\n===== Arquivo =====\n")

    if recommended_camera:
        new_camera_config = {
            "camera_index": recommended_camera["index"],
            "frame_width": r_width,
            "frame_height": r_height,
            "fps": recommended_camera["capabilities"]["fps"],
            "Local_VL_url": vl_url,  # Valor
            "VLapi_key": vl_api_key,  # Valor
            "models": model,  # Valor
        }

        print("de:")
        print(json.dumps(new_camera_config, indent=2, ensure_ascii=False))

        # Conversão
        print("\n===== Conversão =====\n")
        current_index = current_camera_config.get("camera_index")
        current_width = current_camera_config.get("frame_width")
        current_height = current_camera_config.get("frame_height")
        current_fps = current_camera_config.get("fps")

        changes = []
        if current_index != recommended_camera["index"]:
            changes.append(
                f": {current_index} → {recommended_camera['index']}"
            )
        if current_width != r_width or current_height != r_height:
            changes.append(
                f": {current_width}x{current_height} → {r_width}x{r_height}"
            )
        if current_fps != recommended_camera["capabilities"]["fps"]:
            changes.append(
                f"Quadros: {current_fps} → {recommended_camera['capabilities']['fps']}"
            )

        if changes:
            print("paraConversão:")
            for change in changes:
                print(f"  - {change}")
        else:
            print("com，")

        # Arquivo
        if changes:
            print("\nArquivoEmde？(y/n): ", end="")
            choice = input().strip().lower()

            if choice == "y":
                try:
                    # UsandoConfigManager
                    success = config_manager.update_config("CAMERA", new_camera_config)

                    if success:
                        print("\n✓ JáSucessoparaconfig.json!")
                        print("\n=====  =====\n")
                        updated_config = config_manager.get_config("CAMERA", {})
                        print(json.dumps(updated_config, indent=2, ensure_ascii=False))
                    else:
                        print("\n✗ Falha!")

                except Exception as e:
                    logger.error(f": {e}")
                    print(f"\n✗ : {e}")
            else:
                print("\nNão")
    else:
        print("NãoEncontradode")

    return camera_devices


if __name__ == "__main__":
    try:
        cameras = detect_cameras()
        if cameras:
            print("\npara {len(cameras)} Dispositivo！")
        else:
            print("\nNãoparadeDispositivo！")
    except Exception:
        logger.error("Em: {e}")
        print("Em: {e}")
