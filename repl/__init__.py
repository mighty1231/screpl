"""initialize repl"""
from .utils import (
    EPDConstString,
    f_raise_error,
    f_raise_warning,
    f_printf,
    f_strlen,
    StaticStruct,
    Array
)

from .base import (
    ReferenceTable,
    SearchTable,
    EUDByteRW,
    ArgEncoderPtr
)

from .resources.encoder.const import (
    argEncNumber,
    argEncCount,
    argEncModifier,
    argEncAllyStatus,
    argEncComparison,
    argEncOrder,
    argEncPlayer,
    argEncPropState,
    argEncResource,
    argEncScore,
    argEncSwitchAction,
    argEncSwitchState
)

from .resources.encoder.str import (
    argEncAIScript,
    argEncSwitch,
)

from .resources.encoder.condition import encodeCondition_epd
from .resources.encoder.action import encodeAction_epd

from .resources.writer import (
    write_unit,
    writeLocation,
    writeAIScript,
    writeSwitch,
    writeString
)

from .resources.writer.condition import writeCondition_epd
from .resources.writer.action import write_action_epd

from .resources.table.tables import (
    GetLocationNameEPDPointer,
    SetLocationName,
    GetDefaultUnitNameEPDPointer
)

from .core import (
    Application,
    get_app_manager,

    AppCommand,
    runAppCommand,

    AppMethod,
    AppTypedMethod,
)

from .monitor.profile import (
    REPLMonitorPush,
    REPLMonitorPop
)

from .monitor.func import (
    REPLMonitorF,
    REPLMonitorEUDFunc,
    REPLMonitorAppMethod,
    REPLMonitorAppCommand
)

from .apps import (
    StaticApp,
    ScrollApp,
    Logger,
    REPL,
    ChatReaderApp,
    AIScriptSelectorApp,
    ModifierSelectorApp,
    AllyStatusSelectorApp,
    ComparisonSelectorApp,
    OrderSelectorApp,
    PlayerSelectorApp,
    PropStateSelectorApp,
    ResourceSelectorApp,
    ScoreSelectorApp,
    SwitchActionSelectorApp,
    SwitchStateSelectorApp
)
