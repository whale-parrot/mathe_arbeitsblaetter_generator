# build.py
import os
import sys
import PyInstaller.__main__
import streamlit

# os.pathsep is ':' on Linux/Mac and ';' on Windows
sep = os.pathsep

# 1. Find the path to the streamlit package
streamlit_dir = os.path.dirname(streamlit.__file__)
static_dir = os.path.join(streamlit_dir, "static")
runtime_dir = os.path.join(streamlit_dir, "runtime")

print(f"Building for {sys.platform} with separator '{sep}'...")
print(f"Adding Streamlit static and runtime folders...")


PyInstaller.__main__.run([
    '--clean',
    '--onefile',
    f'--add-data=icons{sep}icons',
    f'--add-data=fonts{sep}fonts',
    f'--add-data=app.py{sep}.',
    f'--add-data=generator.py{sep}.',

    # Add the missing Streamlit static and runtime folders
    f'--add-data={static_dir}{sep}streamlit/static',
    f'--add-data={runtime_dir}{sep}streamlit/runtime',
    '--copy-metadata=streamlit',

    # Force PyInstaller to bundle libraries used in app.py/generator.py
    # Because Streamlit loads these dynamically, PyInstaller misses them automatically
    '--collect-all=reportlab',
    '--collect-all=svglib',
    '--collect-all=pymupdf',
    
    # Also add them as hidden imports just to be safe
    '--hidden-import=reportlab',
    '--hidden-import=svglib',
    '--hidden-import=pymupdf',
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=altair',

    '--name=math-worksheets',
    'launcher.py'
])
print("Build complete!")