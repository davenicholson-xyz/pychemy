# pyvista

A fast, keyboard-friendly desktop wallpaper browser for [Wallhaven](https://wallhaven.cc). Browse, search, preview, and set wallpapers without leaving your keyboard.

![pyvista screenshot](https://wallhaven.cc/favicon.ico)

## Features

- Browse wallpapers by **Hot**, **Toplist**, **Latest**, or **Random**
- **Search** the full Wallhaven catalog
- **Collections** support — browse your saved Wallhaven collections
- **Lightbox preview** with resolution, file size, tags, colors, and uploader info
- Infinite scroll with lazy-loaded thumbnails
- Run a custom script to set wallpapers (integrates with any wallpaper setter)
- Vim-style keyboard navigation (`hjkl`)
- Dark theme with minimal UI chrome

## Requirements

- Python 3.11+
- `pywebview`
- `PyQt5` or `PyQt6`

## Installation

### Nix (recommended)

```bash
nix run github:davenicholson-xyz/pyvista
```

Or clone and run:

```bash
nix develop
python main.py
```

### pip

```bash
pip install pywebview PyQt6
python main.py
```

## Configuration

Create `~/.config/pyvista/config.toml`:

```toml
api_key    = "your_wallhaven_api_key"   # Required for collections and NSFW
username   = "your_wallhaven_username"  # Required for collections
query      = ""                          # Default search query
categories = "111"                       # General, Anime, People (bitmask)
purity     = "100"                       # SFW/Sketchy/NSFW (bitmask)
thumb-size = "m"                         # xs | sm | m | l | xl
script     = "/path/to/set-wallpaper.sh" # Script to run on selection
close-on-select = false
output     = false                       # Print filepath to stdout on selection
```

The selected wallpaper's local cache path is passed as the first argument to your script.

## Usage

```bash
python main.py [options]
```

| Flag | Description |
|------|-------------|
| `--api-key KEY` | Wallhaven API key |
| `--username USER` | Wallhaven username |
| `--query QUERY` | Initial search query |
| `--categories BITS` | Category bitmask (e.g. `111`) |
| `--purity BITS` | Purity bitmask (e.g. `100`) |
| `--thumb-size SIZE` | Thumbnail size (`xs` `sm` `m` `l` `xl`) |
| `--min-resolution RES` | Minimum resolution (e.g. `1920x1080`) |
| `--script PATH` | Script to run on selection |
| `--close-on-select` | Close window after setting wallpaper |
| `--output` | Print wallpaper path to stdout |
| `--hot` / `--latest` / `--top` / `--random` | Initial sort mode |
| `--collection NAME` | Open a specific collection on launch |

## Keybindings

| Key | Action |
|-----|--------|
| `h j k l` / arrows | Navigate gallery |
| `Enter` | Run script on selected wallpaper |
| `P` | Preview (lightbox) |
| `O` | Open in browser |
| `S` / `/` | Search |
| `C` | Collections |
| `H` | Sort: Hot |
| `T` | Sort: Toplist |
| `L` | Sort: Latest |
| `R` | Sort: Random |
| `?` | Help |
| `Esc` | Close modal / Quit |

## Cache

Downloaded wallpapers are cached to `~/.cache/pyvista/`.

## License

MIT
