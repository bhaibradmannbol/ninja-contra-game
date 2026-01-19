# Ninja Contra - Zombie Apocalypse

A Contra-style side-scrolling shooter built with Python and Pygame featuring ninja warriors fighting zombies across multiple themed levels.

## Features

### Characters
- **2 Playable Ninjas** with full sprite animations
- Character selection menu with preview
- Idle, run, jump, and attack animations
- Kunai throwing weapons

### Gameplay
- **Multiple Levels** with different themes:
  - Level 1: Graveyard theme with tombstones and dead trees
  - Level 2+: Sci-fi theme with futuristic platforms and objects
- **Zombie Enemies** with walk, idle, attack, and death animations
- **Melee Combat** - zombies attack on contact (no projectiles)
- **Power-ups**: Spread shot, rapid fire, health, extra lives
- **Parallax Backgrounds** with themed decorations
- **Camera System** with smooth scrolling

### Controls
- **Arrow Keys**: Move left/right
- **Space**: Jump
- **Z**: Shoot kunai
- **P**: Pause/unpause
- **Esc**: Return to menu (when paused)
- **R**: Restart (when game over)
- **Enter**: Confirm selections

### Menu System
- Main menu with animated background
- Character selection screen
- Pause menu functionality

## Installation & Setup

### Requirements
```bash
pip install pygame
```

### Run the Game
```bash
python main.py
```

## Game Structure

```
contra_game/
├── main.py                 # Main game file
├── assets/
│   ├── sprites/
│   │   ├── player1/        # First ninja character
│   │   ├── player2/        # Second ninja character
│   │   ├── enemy_male/     # Male zombie sprites
│   │   ├── enemy_female/   # Female zombie sprites
│   │   ├── scifi_objects/  # Sci-fi decorations
│   │   └── *.png          # Graveyard decorations
│   ├── tiles/
│   │   ├── scifi/         # Sci-fi platform tiles
│   │   └── *.png          # Graveyard tiles
│   ├── backgrounds/       # Background images
│   └── sounds/           # Sound effects (optional)
├── README.md
└── requirements.txt
```

## Asset Credits

- **Ninja Sprites**: Custom animated character sheets
- **Zombie Sprites**: Male and female zombie animation sets
- **Graveyard Tileset**: Gothic/cemetery themed platforms and objects
- **Sci-fi Tileset**: Futuristic platform and decoration assets
- **Sound Effects**: 8-bit retro game sounds (optional)

## Technical Features

- **Sprite Animation System**: Frame-based animations with timing
- **Physics Engine**: Gravity, collision detection, platform mechanics
- **Camera System**: Smooth scrolling with level boundaries
- **Asset Management**: Dynamic loading with fallback graphics
- **Theme System**: Level-based visual themes
- **Sound Management**: Optional audio with fallback silence

## Development

The game is built using object-oriented design with separate classes for:
- `Player`: Character control and animation
- `Enemy`: Zombie AI and behavior
- `Level`: Level generation and theme management
- `Camera`: Viewport and scrolling
- `Background`: Parallax backgrounds and decorations
- `Platform`: Tileset-based platform rendering

## Future Enhancements

- Additional character types
- More enemy varieties
- Boss battles
- Additional levels and themes
- Multiplayer support
- Save/load system
- High score tracking

---

**Genre**: Action/Platformer  
**Platform**: Cross-platform (Python/Pygame)  
**Players**: Single-player  
**Rating**: All ages
