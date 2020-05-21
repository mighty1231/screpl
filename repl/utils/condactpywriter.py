condstr = \
'''
def CountdownTimer(Comparison, Time):
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)

def Command(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)

def Bring(Player, Comparison, Number, Unit, Location):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)

def Accumulate(Player, Comparison, Number, ResourceType):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)

def Kills(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)

def CommandMost(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)

def CommandMostAt(Unit, Location):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)

def MostKills(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)

def HighestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 9, ScoreType, 0)

def MostResources(ResourceType):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)

def Switch(Switch, State):
    Switch = EncodeSwitch(Switch, issueError=True)
    State = EncodeSwitchState(State, issueError=True)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)

def ElapsedTime(Comparison, Time):
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)

def Opponents(Player, Comparison, Number):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)

def Deaths(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)

def CommandLeast(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)

def CommandLeastAt(Unit, Location):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)

def LeastKills(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)

def LowestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 19, ScoreType, 0)

def LeastResources(ResourceType):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)

def Score(Player, ScoreType, Comparison, Number):
    Player = EncodePlayer(Player, issueError=True)
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 21, ScoreType, 0)

def Always():
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)

def Never():
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)

'''

# Something specials
condstr2 = \
'''
def DeathsX(Player, Comparison, Number, Unit, Mask):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx=True)

def Memory(dest, cmptype, value):
    return Deaths(EPD(dest), cmptype, value, 0)

def MemoryEPD(dest, cmptype, value):
    return Deaths(dest, cmptype, value, 0)

def MemoryX(dest, cmptype, value, mask):
    return DeathsX(EPD(dest), cmptype, value, 0, mask)

def MemoryXEPD(dest, cmptype, value, mask):
    return DeathsX(dest, cmptype, value, 0, mask)
'''

actstr = \
'''

def Victory():
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat():
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger():
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(Time):
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(Unit, Where, WAVName, TimeModifier, Time, Text, AlwaysDisplay):
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    WAVName = EncodeString(WAVName, issueError=True)
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    Text = EncodeString(Text, issueError=True)
    return Action(Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, AlwaysDisplay)


def PlayWAV(WAVName):
    WAVName = EncodeString(WAVName, issueError=True)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text, AlwaysDisplay):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, AlwaysDisplay)


def CenterView(Where):
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(Count, Unit, Where, Player, Properties):
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    Properties = EncodeProperty(Properties, issueError=True)
    return Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch, State):
    Switch = EncodeSwitch(Switch, issueError=True)
    State = EncodeSwitchAction(State, issueError=True)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier, Time):
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script):
    Script = EncodeAIScript(Script, issueError=True)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script, Where):
    Script = EncodeAIScript(Script, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit, Location, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType, Label):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(ScoreType, Label):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ScoreType, 21, 0, 4)


def KillUnit(Unit, Player):
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit, Player):
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player, Modifier, Amount, ResourceType):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player, Modifier, Amount, ScoreType):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ScoreType, 27, Modifier, 4)


def MinimapPing(Where):
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit, Time):
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State):
    State = EncodePropState(State, issueError=True)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal, Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal, Unit, Location, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal, ResourceType, Label):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal, Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal, ScoreType, Label):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ScoreType, 37, 0, 4)


def MoveLocation(Location, OnUnit, Owner, DestLocation):
    Location = EncodeLocation(Location, issueError=True)
    OnUnit = EncodeUnit(OnUnit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation):
    Count = EncodeCount(Count, issueError=True)
    UnitType = EncodeUnit(UnitType, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal):
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName):
    ScenarioName = EncodeString(ScenarioName, issueError=True)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State, Unit, Owner, Where):
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State, Unit, Owner, Where):
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number, Unit, Where, ForPlayer):
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player, Modifier, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(Unit, Owner, StartLocation, OrderType, DestLocation):
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    OrderType = EncodeOrder(OrderType, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, OrderType, 20)


def Comment(Text):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count, Unit, Owner, Where, NewOwner):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    NewOwner = EncodePlayer(NewOwner, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count, Owner, Where, NewValue):
    Count = EncodeCount(Count, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(Add, Count, Unit, Owner, Where):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Add, Unit, 53, Count, 20)


def PauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw():
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(Player, Status):
    Player = EncodePlayer(Player, issueError=True)
    Status = EncodeAllyStatus(Status, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)
'''

actstr2 = \
'''
def SetMemory(dest, modtype, value):
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, EPD(dest), value, 0, 45, modtype, 20)


def SetMemoryEPD(dest, modtype, value):
    dest = EncodePlayer(dest, issueError=True)
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, dest, value, 0, 45, modtype, 20)


def SetNextPtr(trg, dest):
    return SetMemory(trg + 4, 7, dest)


def SetDeathsX(Player, Modifier, Number, Unit, Mask):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx=True)


def SetMemoryX(dest, modtype, value, mask):
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(mask, 0, 0, 0, EPD(dest), value, 0, 45, modtype, 20, eudx=True)


def SetMemoryXEPD(dest, modtype, value, mask):
    dest = EncodePlayer(dest, issueError=True)
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(mask, 0, 0, 0, dest, value, 0, 45, modtype, 20, eudx=True)
'''


class Cond:
	def __init__(self, name, args, codedict, condargs):
		'''
		name: name of condition
		args: list of str, arg names on each stockcond
		codedict: dict args->encoding/decoding name
		condargs: list of str/int, args to Condition
		'''
		self.name = name
		self.args = args
		self.codedict = codedict
		self.condargs = condargs

		assert all([k in self.args for k in self.codedict]), (self.name, self.args, self.codedict)
		assert all([k in self.args for k in condargs if type(k) is str])

	def __repr__(self):
		s = '{}({}) = Condition({})'.format(
			self.name,
			', '.join(['{}:{}'.format(a, self.codedict[a]) \
				if a in self.codedict \
				else a for a in self.args]),
			self.condargs
		)
		return s

class Act:
	def __init__(self, name, args, codedict, actargs):
		'''
		name: name of action
		args: list of str, arg names on each stockcond
		codedict: dict args->encoding/decoding name
		actargs: list of str/int, args to Action
		'''
		self.name = name
		self.args = args
		self.codedict = codedict
		self.actargs = actargs

		assert all([k in self.args for k in self.codedict]), (self.name, self.args, self.codedict)
		assert all([k in self.args for k in actargs if type(k) is str]), actargs

	def __repr__(self):
		s = '{}({}) = Action({})'.format(
			self.name,
			', '.join(['{}:{}'.format(a, self.codedict[a]) \
				if a in self.codedict \
				else a for a in self.args]),
			self.actargs
		)
		return s

def _condparse():
	global condstr
	conds = []
	
	name = ''
	args = []
	codedict = {}
	for line in condstr.split('\n'):
		if line.startswith('def '):
			# Start of condition
			name = line[4:line.index('(')]
			_argpart = line[line.index('(')+1 : line.index(')')]
			_args = _argpart.split(',')
			args = list(map(lambda t:t.strip(), _args))

			if args == ['']:
				args = []

		elif line.startswith('    return'):
			# wrap-up
			_argpart = line[line.index('(')+1 : line.index(')')]
			condargs = []
			for arg in _argpart.split(','):
				arg = arg.strip()
				try:
					arg = int(arg)
				except ValueError:
					pass
				finally:
					condargs.append(arg)

			conds.append(Cond(name, args, codedict, condargs))

			name = ''
			args = []
			codedict = {}

		elif line == '':
			continue

		else:
			# encoders
			argname = line[:line.index('=')].strip()
			codename = line[line.index('=')+1:line.index('(')].strip()
			assert codename.startswith('Encode'), codename
			codename = codename[6:]
			codedict[argname] = codename

	return conds

def _actparse():
	global actstr
	acts = []
	
	name = ''
	args = []
	codedict = {}
	for line in actstr.split('\n'):
		if line.startswith('def '):
			# Start of condition
			name = line[4:line.index('(')]
			print(line)
			_argpart = line[line.index('(')+1 : line.index(')')]
			_args = _argpart.split(',')
			args = list(map(lambda t:t.strip(), _args))

			if args == ['']:
				args = []

		elif line.startswith('    return'):
			# wrap-up
			_argpart = line[line.index('(')+1 : line.index(')')]
			actargs = []
			for arg in _argpart.split(','):
				arg = arg.strip()
				try:
					arg = int(arg)
				except ValueError:
					pass
				finally:
					actargs.append(arg)

			acts.append(Act(name, args, codedict, actargs))

			name = ''
			args = []
			codedict = {}

		elif line == '':
			continue

		else:
			# encoders
			argname = line[:line.index('=')].strip()
			codename = line[line.index('=')+1:line.index('(')].strip()
			assert codename.startswith('Encode'), codename
			codename = codename[6:]
			codedict[argname] = codename

	return acts

def writecond():
	conds = _condparse()
	condm = ["locid", "player", "amount", "unitid", "comparison",
		"condtype", "restype", "flags","internal"]
	s = ''
	for cond in conds:
		s += '@EUDFunc\n'
		s += 'def dec_{}(epd):\n'.format(cond.name)

		if len(cond.args) == 0:
			# no args like Always()
			s += '\t_output_writer.write_f("{}()")'.format(cond.name)
		else:
			s += '\tm = _condmap(epd)\n'
			s += '\t_output_writer.write_f("{}(")\n'.format(cond.name)
			for i, arg in enumerate(cond.args):
				if arg in cond.codedict:
					# encode
					coder = cond.codedict[arg]
					if coder in ['Unit', 'Location', 'AIScript', 'Switch', 'String']:
						s += '\twrite{}(m.{})\n'.format(
							coder, condm[cond.condargs.index(arg)])
					else:
						s += '\twrite_constant(EPD(tb_{}), m.{})\n'.format(
							cond.codedict[arg], condm[cond.condargs.index(arg)])
				else:
					s += '\t_output_writer.write_decimal(m.{})\n'.format(
						condm[cond.condargs.index(arg)])

				if i < len(cond.args) - 1:
					s += '\t_output_writer.write_f(", ")\n'
				else:
					s += '\t_output_writer.write_f(")")\n'
		s += '\n\n'

	print(s)

	v = [0 for _ in range(24)]
	for cond in conds:
		v[cond.condargs[5]] = "dec_" + cond.name
	print(v)


def writeact():
	acts = _actparse()
	actm = ["locid1", "strid", "wavid", "time", "player1", "player2",
		"unitid", "acttype", "amount", "flags"]

	s = ''
	for act in acts:
		s += '@EUDFunc\n'
		s += 'def dec_{}(epd):\n'.format(act.name)

		if len(act.args) == 0:
			# no args like Always()
			s += '\t_output_writer.write_f("{}()")'.format(act.name)
		else:
			s += '\tm = _actmap(epd)\n'
			s += '\t_output_writer.write_f("{}(")\n'.format(act.name)
			for i, arg in enumerate(act.args):
				if arg in act.codedict:
					# encode
					coder = act.codedict[arg]
					pr = actm[act.actargs.index(arg)]
					if coder in ['Unit', 'Location', 'AIScript', 'Switch', 'String']:
						s += '\twrite{}(m.{})\n'.format(
							coder, pr)
					elif coder == 'Count':
						s += '\tif EUDIf()(m.{} == 0):\n'.format(pr)
						s += '\t\t_output_writer.write_f("All")\n'
						s += '\tif EUDElse()():\n'
						s += '\t\t_output_writer.write_decimal(m.{})\n'.format(pr)
						s += '\tEUDEndIf()\n'
					elif coder == 'Property':
						s += '\t_output_writer.write_decimal(m.{}) # @TODO property\n'.format(pr)
					else:
						s += '\twrite_constant(EPD(tb_{}), m.{})\n'.format(
							act.codedict[arg], pr)
				else:
					s += '\t_output_writer.write_decimal(m.{})\n'.format(
						actm[act.actargs.index(arg)])

				if i < len(act.args) - 1:
					s += '\t_output_writer.write_f(", ")\n'
				else:
					s += '\t_output_writer.write_f(")")\n'
		s += '\n\n'

	print(s)

	v = [0 for _ in range(58)]
	for act in acts:
		v[act.actargs[7]] = "dec_" + act.name
	print(v)

if __name__ == "__main__":
	writeact()
