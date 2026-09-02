# build.py

import os
import sys
import PyInstaller.__main__
import streamlit

# os.pathsep is ':' on Linux/Mac and ';' on Windows
sep = os.pathsep

# Find Streamlit package paths
streamlit_dir = os.path.dirname(streamlit.__file__)
static_dir = os.path.join(streamlit_dir, "static")
runtime_dir = os.path.join(streamlit_dir, "runtime")

print(f"Building for {sys.platform} with separator '{sep}'...")
print("Adding Streamlit static and runtime folders...")

# Platform-specific application name
if sys.platform == "win32":
    app_name = "math-worksheets-windows"
elif sys.platform == "darwin":
    app_name = "math-worksheets-macos"
else:
    app_name = "math-worksheets-linux"

# Base arguments
args = [
    "--clean",
    f"--name={app_name}",
]

# Build type
if sys.platform == "darwin":
    # Creates math-worksheets-macos.app
    args.append("--windowed")
else:
    # Creates a single executable
    args.append("--onefile")

# Application files and dependencies
args.extend([
    f"--add-data=icons{sep}icons",
    f"--add-data=fonts{sep}fonts",
    f"--add-data=app.py{sep}.",
    f"--add-data=generator.py{sep}.",

    # Streamlit runtime files
    f"--add-data={static_dir}{sep}streamlit/static",
    f"--add-data={runtime_dir}{sep}streamlit/runtime",
    "--copy-metadata=streamlit",

    # Dynamically loaded packages
    "--collect-all=reportlab",
    "--collect-all=svglib",
    "--collect-all=pymupdf",

    # Hidden imports
    "--hidden-import=reportlab",
    "--hidden-import=svglib",
    "--hidden-import=pymupdf",
    "--hidden-import=pandas",
    "--hidden-import=numpy",
    "--hidden-import=altair",

    # Entry point
    "launcher.py"
])

PyInstaller.__main__.run(args)

print("Build complete!")
