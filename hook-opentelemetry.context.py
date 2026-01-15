# Ensure opentelemetry context backends are collected
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("opentelemetry.context")

