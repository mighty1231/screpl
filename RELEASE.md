# Release 1.1.0

## Major Features and Improvements
* new plugin `cunit`
  * supports to analyze arbitrary CUnit structure
* new plugin `dump`
  * supports to dump memory in SC to `bridge`
* new plugin `test`
  * used on test several features
  * `ArrayTestApp` and `MonitorTestApp` provides unit tests for `Array` and `monitor`
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
  * supports `write_strnepd`
* `bridge`
  * now `blind mode` displays clearer
  * create binary file from selection on app output, may used with `Dump` plugin
* plugin `string`
  * new options to export for `eudplib` and `EUDEditor`
  * editor supports to input indent and newline with `\t` and `\n`
  * editor supports to move cursor with keyboard - `Home` and `End`

## Bug Fixes and Other Changes
* `AppManager` - removed usage of `DBString`, improved stability on managing game texts
* `ScrollApp` - fixed initialization
* `StaticApp` - fixed display
* `bridge`
  * improved stability
  * now managed with `block` objects for better scability
* changed class name `_AppMethod`, `_AppCommand` to `AppMethodN`, `AppCommandN`, respectively
* plugin `variable` - properly overrides `onInit()`

