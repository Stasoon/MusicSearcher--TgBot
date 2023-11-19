import random


def get_vk_user_agent() -> str:
    agents = (
        'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)',
        'KateMobileAndroid/56 lite-460 (Android 6.0; SDK 23; x86; unknown Android SDK built for x86; ru)',
        'KateMobileAndroid/56 (Android 9.2; SDK 22; x86; unknown Android SDK built for x64; fr)',
        'KateMobileAndroid/56 lite-640 (iOS 17; SDK 20; x64; unknown Android SDK built for x64; ru)',
        'KateMobileAndroid/56 (iOS 18; SDK 20; x64; unknown Android SDK built for x64; fr)',
        'KateMobileAndroid/56 lite-460 (iOS 15; SDK 20; x64; unknown Android SDK built for x86; en)',
    )
    return random.choice(agents)
