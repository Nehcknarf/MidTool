from pathlib import Path

# .qrc
p = Path(".")
for qml_file in p.glob('**/*.qml'):
    line = f"<file>{qml_file}</file>"
    print(line)

p = Path(".")
for qmldir_file in p.glob('**/qmldir'):
    line = f"<file>{qmldir_file}</file>"
    print(line)

for font_file in p.glob('**/*.ttf'):
    line = f"<file>{font_file}</file>"
    print(line)

q = p / "content" / "images"
for image in q.iterdir():
    line = f"<file>{image}</file>"
    print(line)

# .pyproject
p = Path(".")
for qml_file in p.glob('**/*.py'):
    print(f"\"{qml_file}\",")
for qml_file in p.glob('**/*.qml'):
    print(f"\"{qml_file}\",")