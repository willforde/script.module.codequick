from addondev import initializer
import os

# Initialize mock kodi environment
initializer(os.path.join(os.path.dirname(os.path.dirname(__file__)), "script.module.codequick"))
