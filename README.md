# SC-REPL

SC-REPL provides command line interface and text UI based application framework on StarCraft I UMS maps, built on [euddraft](https://github.com/armoha/euddraft).

It helps to debug UMS maps in Starcraft I.

## Example

You can debug your map easily and effectively using `Application`. For example,

```python
class MyApp(Application):
    def loop(self):
        if EUDIf()(get_app_manager().key_press("ESC")):
            get_app_manager().request_destruct()
            EUDReturn()
        EUDEndIf()
        get_app_manager().request_update()

    def print(self, writer):
        # get hit point of unit 0
        hit_point_of_unit_0 = f_dwread_epd(EPD(0x59CCB0))
        writer.write_f("%D\n", hit_point_of_unit_0)
        writer.write(0) # null-end

@AppCommand
def starting_command(self):
    get_app_manager().start_application(MyApp)

REPL.add_command("hpcheck", starting_command)
```

Above lines of codes enable your UMS map display the HP of specific unit continously, if you chat `hpcheck()`.

There are some standard plugins, and corresponding demo videos.

* `sample` plugin - [video](https://youtu.be/6RexCF3SBFU), [source](example/sample/myapp.py)
* `location` plugin - [video](https://youtu.be/f3M0CDGIX2A), [source](screpl/plugins/location)
* `boundeditor` plugin - [video](https://youtu.be/c_VYYc7Ozy8), [source](screpl/plugins/boundeditor
)
* `variable` and `string`  plugin - [video](https://youtu.be/s9jIWKP2bfE)

There are many amazing features other than them. `bridge` enables to communicate applications by using remote client.

## Installation

### Required

* Starcraft I Remastered
* [euddraft](https://github.com/armoha/euddraft) version >= 0.8.9.9

### Instruction

* Install one of [release versions](https://github.com/mighty1231/screpl/releases)
* Move a directory `screpl` to `euddraft/lib`.
* Move a file `prepl.py` to `euddraft/plugins`.

```bash
euddraft0.*.*.*
├── lib
│   └── screpl
│       ├── apps
│       ├── bridge_server
│       ├── core
│       └── ...
├── plugins
│   └── prepl.py
└── euddraft.exe
```

* You may install *SC-REPL Bridge Client* if you want.

## Apply SC-REPL on your map

1. Append following text in your euddraft project file (\*.edd).

```
[prepl]
superuser: P1
plugins: screpl.plugins.location screpl.plugins.string screpl.plugins.cunit
```
* Check [how to write edd file](https://github.com/mighty1231/screpl/wiki/How-to-write-edd-file)

2. Run your euddraft project file with euddraft.

## Plugins

You can make your customized application as a plugin of SC-REPL. Check it [here](https://github.com/mighty1231/screplPluginTemplate).


## Documentation

You can check [doc](https://mighty1231.github.io/screpl/) to get information on functions.

High-level documentations (application level) are provided with [Github wiki](https://github.com/mighty1231/screpl/wiki), but so far, most of them are written in Korean.

## Contribution Guide

You can contribute to this project. Check [contribution guide](CONTRIBUTING.md).

## LICENSE

MIT License
