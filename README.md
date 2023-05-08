# Yet Another Game Development Entity

Implementation of client for turn-based hexagonal-map game about tank battles. Game is final project for WG Forge SE course. Client is equipped with game AI and GUI.

## Team members

- [Mikhail Vorobev](https://github.com/InversionSpaces)

- [Aleksa Ristić](https://github.com/NORT0X)

- [Aleksandar Marinković](https://github.com/AkiMar1510)

## Requirements

- `python >= 3.11` 
- `pygame`

## Installing

```sh
python3 -m pip install -r requirements.txt
```

## Running

```sh
python3 main.py
```

Login details, number of bots started and GUI parameters could be modified in `main.py`.

**TODO**: add cli parameters for that.

## Running tests

```sh
python -m unittest discover -s tests
```

## Project structure

- `client` - implementation of a client for the game server
  (`session.py` contains primary `Session` class)
- `model` - internal game model for implementation of AI
- `ai` - utils for AI implementation
- `player` - implementation of AI engine
  (`engine.py` contains primary `Engine` class)
- `graphics` - implementation of GUI
  (`window.py` contains primary `Window` class)
- `tests` - unit tests
