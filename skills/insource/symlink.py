from pathlib import Path

from tqdm import tqdm


cwd = Path.cwd()
links_dir = cwd / "links"
links_dir.mkdir(exist_ok=True)

directories = [
    path
    for path in cwd.iterdir()
    if path.is_dir()
    and not path.is_symlink()
    and path != links_dir
]

for directory in tqdm(directories, desc="Creating symlinks"):
    link = links_dir / directory.name

    if link.exists() or link.is_symlink():
        continue

    link.symlink_to(directory, target_is_directory=True)