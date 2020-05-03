# SC-REPL

SC-REPL is a text-UI framework on StarCraft I UMS maps, built on [euddraft](https://github.com/armoha/euddraft).

It helps to debug UMS maps in Starcraft I.

## Example

UMS maps applied SC-ERPL with...

* `location` plugin - [video](https://youtu.be/f3M0CDGIX2A)
, [source](https://github.com/mighty1231/screpl/tree/master/plugins/location)
* `sample` plugin - [video](https://www.youtube.com/watch?v=6RexCF3SBFU), [source](https://github.com/mighty1231/screpl/blob/master/example/sample/myapp.py)

## Required

* Starcraft I Remastered
* [euddraft](https://github.com/armoha/euddraft) version >= 0.8.9.9


## Installation
* Install one of [release versions](https://github.com/mighty1231/screpl/releases)
* Move a directory `repl` and `plugins` to `euddraft/lib`.
* Move a file `prepl.py` to `euddraft/plugins`.

```bash
euddraft0.*.*.*
├── lib
│   ├── repl
│   │   ├── apps
│   │   ├── base
│   │   └── ...
│   └── plugins //plugins of repl
│       ├── location
│       ├── memory
│       └── ...
├── plugins //plugins of euddraft
│   └── prepl.py
└── euddraft.exe
```

* You may install *SC-REPL Bridge Client* if you want.

## Apply SC-REPL on your map

1. Append following text in your euddraft project file (\*.edd).

```
[prepl.py]
superuser: P1
plugins: plugins.location plugins.memory plugins.variable
```
* Check [how to write edd file](https://github.com/mighty1231/screpl/wiki/How-to-write-edd-file)

2. Run your euddraft project file with euddraft.

## Plugins

You can make your customized application as a plugin of SC-REPL. Check it [here](https://github.com/mighty1231/screplPluginTemplate).


## Documentation

Documentation is provided with [Github wiki](https://github.com/mighty1231/screpl/wiki)

## Contribution Guide

You may make your own plugin, but also you can contribute to this project. Check [contribution guide](CONTRIBUTING.md).


## LICENSE

MIT License
