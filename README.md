# SC-REPL

SC-REPL is a plugin for [euddraft](https://github.com/armoha/euddraft)

It helps to debug UMS maps in Starcraft I.

Unlike other plugins, SC-REPL manages detailed plugins (app) on its own.



## Example

* with location application - [video](https://youtu.be/f3M0CDGIX2A)
and corresponding [source](https://github.com/mighty1231/screpl/tree/master/apps/location)
* with sample application - [video](https://www.youtube.com/watch?v=6RexCF3SBFU)
and corresponding [source](https://github.com/mighty1231/screpl/blob/master/example/sample/myapp.py)

## Contribution [Guide](CONTRIBUTING.md)


## Required

* Starcraft I Remastered
* [euddraft](https://github.com/armoha/euddraft) version >= 0.8.9.9


## Installation

* Move folders `repl` and `apps` to `euddraft/lib`.
* Move a file `prepl.py` to `euddraft/plugins`.

```bash
euddraft0.*.*.*
├── lib
│   ├── repl
│   └── apps
├── plugins
│   └── prepl.py
└── euddraft.exe
```

## How to build

1. Append following text in your euddraft project file (\*.edd).

```
[prepl.py]
superuser: P1
plugins: apps.location apps.memory
```

2. Run your euddraft project file with euddraft.

## Plugins

You can make your customized application as a plugin of SC-REPL. Check it [here](https://github.com/mighty1231/screplPluginTemplate).

