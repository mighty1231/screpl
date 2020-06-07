# Release 1.1.3

## Major Features and Improvements
* new plugin `switch` supports to show switch status
* new paradigm *manual* mode
  * pressing key F1 shows the manual text of the app
* plugin `boundeditor`
  * `DetailedActionApp` links to `TrigActionEditorApp` to modify action
* plugin `cunit`
  * `CUnitOptionApp` provides bwapi comments for each members
* plugin `location`
  * `LocationEditorApp` provides *manual* mode
* plugin `string`
  * `StringEditorApp` provides *manual* mode
  * supports to input unicode character
* plugin `trigger`
  * provides *manual* mode
  * shows value of trigger flag
  * new commands
    * to edit a trigger entry
    * to add a new trigger entry
    * to set flag value
    * to set trigger pointer to arbitrary trigger
    * to set trigger pointer to next trigger
  * new application `TrigConditionEditorApp` and `TrigActionEditorApp`
    * provides *manual* mode
    * supports to edit each entry with value
    * supports to edit each entry with helper apps

## Bug Fixes and Other Changes
* `ReadNumber` properly reads hexadecimal number
* plugin `trigger`
  * bug fix: provides trigger blocks for each player
  * improved UI
* increased code readability
* `resources`
  * new resource tables - `Property`, `ConditionType`, and `ActionType`
  * provides default names for location and switch
* fixed a crash on `LocationManagerApp`

# Release 1.1.2

## Major Features and Improvements
* new plugin `display`
  * support debugging real-time UI related values
* new plugin `trigger`
  * log conditions of trigger that is commentized with `screpl-condcheck`

## Bug Fixes and Other Changes
* package `utils`
  * `struct.REPLStruct` provides copying method `cpy`
  * `byterw.REPLByteRW` now defines some writing methods dynamically
    * `write_condition_epd`, `write_action_epd`, etc.
  * `debug.f_raise_error` receives variable arguments
  * new function `string.f_memcmp_epd`
* update `bridge`
  * now shared memory region contains the version of protocol
  * now client properly shows `Logger` logs

# Release 1.1.1

## Major Features and Improvements
* run `pylint`
  * changed a lot of namings
  * added docstrings
  * injected dependency on some code
* new plugin system
  * `plugin_setup()` and `plugin_get_dependencies()` must be defined on `__init__.py`
* plugin `cunit` supports `ReadStructApp`
  * enables to export cunit array information to `bridge`

## Bug Fixes and Other Changes
* documentation for some modules, classes and functions
* new class `DisplayWriter` to simply support text UI
* removed `cmd_output_epd` member for default `Application`
  * syntax error for command is logged by `Logger` application
* changed heartbeat signal between `bridge` to use inversed system time
* `AppManager.getWriter()` was removed. Instead, use `main.get_main_writer()`


# Release 1.1.0

## Major Features and Improvements
* new plugin `cunit`
  * supports to analyze arbitrary CUnit structure
* new plugin `dump`
  * supports to dump memory in SC to `bridge`
* new plugin `test`
  * used on test several features
  * `ArrayTestApp` and `MonitorTestApp` provide unit tests for `Array` and `monitor`, respectively
* new feature `monitor`
  * monitors execution time between arbitrary codes
  * monitors input/output or execution time of `EUDFunc`, `AppMethod` and `AppCommand`
  * `REPLMonitorPush`, `REPLMonitorPop`, `REPLMonitorF`
* new class `StaticStruct`
  * similar to `EUDStruct`, but more powerful
* new class `Array`
  * child class of `StaticStruct`, supports array data structure
  * methods available: `at`, `push`, `pop`, `insert`, `delete`, `contains`, `index`, `sort` and `values`
* `EUDByteRW`
  * supports writing signed/unsigned 8/16/32 bit integer
  * new function `write_strnepd`
* `bridge`
  * displays game text under `blind mode` more clear
  * creates binary file from selection on app output, may used with `dump` plugin
* plugin `string`
  * new options to export for `eudplib` and `EUDEditor`
  * editor supports to input indent and newline with `\t` and `\n`
  * editor supports to move cursor with keyboard - `Home` and `End`

## Bug Fixes and Other Changes
* `AppManager` - removed use of `DBString`, improved stability on managing game text
* `ScrollApp` - fixed initialization
* `StaticApp` - fixed display
* `bridge`
  * improved stability
  * now managed with `block` objects for better scability
* changed class name `_AppMethod`, `_AppCommand` to `AppMethodN`, `AppCommandN`, respectively
* plugin `variable` overrides `onInit()` properly

