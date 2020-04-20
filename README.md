# SC-REPL

SC-REPL is a plugin for [euddraft](https://github.com/armoha/euddraft)

It helps to debug UMS maps in Starcraft I.

Unlike other plugins, SC-REPL manages detailed plugins on its own.


## Reqired

* Starcraft I Remastered
* [euddraft](https://github.com/armoha/euddraft) version >= 0.8.9.9


## Installation

* Move a folder `repl` to `euddraft/lib`
* Move a file `prepl.py` to `euddraft/plugins`


## How to build

1. Add following text in your euddraft project file (\*.edd).

```
[prepl.py]
superuser: P1
plugins: some_module
```

Also, you can use multiple modules.

```
plugins: module1 module2 module3
```

2. Run your euddraft project file with euddraft.

## Plugins

You can make your customized application as a plugin of SC-REPL. Check it [here](https://github.com/mighty1231/screplPluginTemplate)

