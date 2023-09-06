sudo apt install ffmpeg

pyside6-rcc resource.qrc -o resource.py

20.04
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
mkdir -p /usr/lib/dri/
sudo ln -s /usr/lib/x86_64-linux-gnu/dri/swrast_dri.so /usr/lib/dri/

22.04
sudo find / -name libpyside6qml*
sudo ln -s /home/z/miniconda3/envs/midtoolNext2204/lib/python3.11/site-packages/PySide6/libpyside6qml.abi3.so.6.5 /lib