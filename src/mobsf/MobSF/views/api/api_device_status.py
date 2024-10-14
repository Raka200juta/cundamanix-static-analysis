import subprocess
from django.http import JsonResponse

# Define the phone-related keywords for USB check
PHONE_KEYWORDS = [
    "Android", "Phone", "Samsung", "Xiaomi", "Huawei", "Nokia", "Qualcomm",
    "OnePlus", "Google", "Pixel", "Sony", "Xperia", "Motorola", "Moto", "Oppo",
    "Vivo", "LG", "ASUS", "Zenfone", "Lenovo", "Realme", "ZTE", "HTC",
    "BlackBerry", "Alcatel", "Meizu", "Micromax", "Spreadtrum", "Snapdragon",
    "Exynos", "Broadcom", "HiSilicon Kirin", "MediaTek"
]


def check_usb_connection():
    """
    Checks if any USB device matches the keywords in PHONE_KEYWORDS.
    """
    try:
        result = subprocess.run(
            ["lsusb"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8").strip()

        lines = output.split("\n")
        for line in lines:
            for keyword in PHONE_KEYWORDS:
                if keyword.lower() in line.lower():
                    return True
        return False
    except Exception as e:
        print(f"Error checking USB connection: {e}")
        return False


def check_adb_connection():
    try:
        result = subprocess.run(
            ["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8").strip()

        lines = output.split("\n")[1:]
        for line in lines:
            if "device" in line:
                return True
        return False
    except Exception as e:
        print(f"Error checking ADB connection: {e}")
        return False


def check_device_status(request):
    is_cable_connected = check_usb_connection()
    is_adb_connected = check_adb_connection()

    return JsonResponse({
        "status": 200,
        "message": "Device status checked successfully",
        "data": {
            "is_cable_connected": is_cable_connected,
            "is_adb_connected": is_adb_connected
        }
    })
