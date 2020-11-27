#DESC	1.2 * DESCRIPTOR INFORMATION ***********************
*
*	Dataset Type and Format:
*
DSRC	EXP
BSEQ	BIG
IKKF	REAL
XTYP	IDX
YTYP	NODATA
ZTYP	NODATA
*
*	Item Formats:
*
IRFMT	D
*
*	Data Ranges and Resolutions:
*
XPTS	3000
XMIN	3501.000000
XWID	30.000000
*
*	Documentational Text:
*
TITL	'BDPA 1D FieldSweep'
IRNAM	'1st Harm Absorption'
XNAM	'Field'
IRUNI	''
XUNI	'G'
*
************************************************************
*
#SPL	1.2 * STANDARD PARAMETER LAYER
*
OPER    xuser
DATE    12/07/20
TIME    14:23:26
CMNT    
SAMP    
SFOR    
STAG    C
EXPT    CW
OXS1    IADC
AXS1    B0VL
AXS2    NONE
AXS3    
A1CT    0.3516
A1SW    0.003
MWFQ    9.852145e+09
MWPW    0.0006325
AVGS    1
SPTP    0.01
RCAG    40
RCHM    1
B0MA    1e-05
B0MF    100000
RCPH    0.0
RCOF    -0.0
A1RS    3000
RCTC    0.00256
*
************************************************************
*
#DSL	1.0 * DEVICE SPECIFIC LAYER
*

.DVC     acqStart, 1.0


.DVC     ezcw, 1.0

MetalIonsDef       False
OrgRadicalsDef     False

.DVC     fieldCtrl, 1.0

AllegroMode        True
CenterField        3516.00 G
Delay              0.0 s
FieldFlyback       On
FieldWait          Wait LED off
GFactor            2.000000
MeasuringHall      False
SetToSampleG       False
StaticFieldMon     3501.000 G
SweepDirection     Up
SweepWidth         30.0 G
WidthTM            200.0 G

.DVC     fieldSweep, 1.0


.DVC     freqCounter, 1.0

FrequencyMon       9.852145 GHz
QMonitBridge       On

.DVC     mwBridge, 1.0

AcqFineTuning      Never
AcqScanFTuning     Off
AcqSliceFTuning    Off
BridgeCalib        49.7
Power              0.6325 mW
PowerAtten         25.0 dB
QValue             6900

.DVC     recorder, 1.0

BaselineCorr       Off
NbScansAcc         1
NbScansDone        1
NbScansToDo        1
ReplaceMode        Off
SmoothMode         Manual
SmoothPoints       0

.DVC     scanEnd, 1.0


.DVC     signalChannel, 1.0

AFCTrap            True
AllegroMode        True
AllowShortCt       False
Calibrated         True
ConvFact           9.271e-09
ConvTime           10.00 ms
DualDetect         OFF
EliDelay           1.0 us
ExtLockIn          False
ExtTrigger         False
Gain               40 dB
Harmonic           1
HighPass           True
Integrator         False
IsCalibExp         False
ModAmp             0.100 G
ModFreq            100.00 kHz
ModInput           Internal
ModPhase           0.0
ModResol           10.000
Offset             -0.0 %
PolyCof            {2;3,9;0} 0,0.99652,0,0,0.00737177,0,0,-0.00559614,0,0,-2.88221e-05,0,0,1.00404e-05,0,0,3.43695e-08,0,0,-5.0404e-09,0,0,-1.4783e-11,0,0,-1.29132e-12,0
ResCenter          62.5 mm
ResLength          40 mm
Resolution         3000
Resonator          1
SctNorm            True
SctRevision        Allegro
SpuExtension       False
SweepTime          30.00 s
TimeConst          2.56 ms
TimeExp            False
TuneCaps           38

*
************************************************************
