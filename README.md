# SC-REPL

SC-REPL is a plugin for [euddraft](https://github.com/armoha/euddraft)

It helps to debug UMS maps in Starcraft I.

Unlike other plugins, SC-REPL manages detailed plugins (app) on its own.



## Example

* using location plugin - [video](https://youtu.be/f3M0CDGIX2A)
and corresponding [source](https://github.com/mighty1231/screpl/tree/master/plugins/location)
* euddraft project with sample plugin - [video](https://www.youtube.com/watch?v=6RexCF3SBFU)
and corresponding [source](https://github.com/mighty1231/screpl/blob/master/example/sample/myapp.py)


## Required

* Starcraft I Remastered
* [euddraft](https://github.com/armoha/euddraft) version >= 0.8.9.9


## Installation

* Move a directory `repl` to `euddraft/lib`
* Move a directory `plugins` to `euddraft/lib` and rename it into `replplugins`.
* Move a file `prepl.py` to `euddraft/plugins`.

```bash
euddraft0.*.*.*
├── lib
│   ├── repl
│   │   ├── apps
│   │   ├── base
│   │   └── ...
│   └── replplugins
│       ├── location
│       └── ...
├── plugins
│   └── prepl.py
└── euddraft.exe
```

## How to build

1. Append following text in your euddraft project file (\*.edd).

```
[prepl.py]
superuser: P1
plugins: replplugins.location replplugins.memory replplugins.variables
```

2. Run your euddraft project file with euddraft.

## Plugins

You can make your customized application as a plugin of SC-REPL. Check it [here](https://github.com/mighty1231/screplPluginTemplate).


## Documentation

Documentation is provided with [wiki](https://github.com/mighty1231/screpl/wiki)

## Contribution Guide

You may make your own plugin, but also you can contribute to this project. Check [contribution guide](CONTRIBUTING.md).


## LICENSE

MIT License
