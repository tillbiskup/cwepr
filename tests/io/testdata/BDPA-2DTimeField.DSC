#DESC	1.2 * DESCRIPTOR INFORMATION ***********************
*
*	Dataset Type and Format:
*
DSRC	EXP
BSEQ	BIG
IKKF	REAL
XTYP	IDX
YTYP	IGD
ZTYP	NODATA
*
*	Item Formats:
*
IRFMT	D
YFMT	D
*
*	Data Ranges and Resolutions:
*
XPTS	2000
XMIN	0.000000
XWID	10.000000
YPTS	20
YMIN	3501.000000
YWID	30.000000
*
*	Documentational Text:
*
TITL	'BDPA 2D TimeField'
IRNAM	'1st Harm Absorption'
XNAM	'Time'
YNAM	'Field'
IRUNI	''
XUNI	's'
YUNI	'G'
*
************************************************************
*
#SPL	1.2 * STANDARD PARAMETER LAYER
*
OPER    xuser
DATE    12/07/20
TIME    14:58:21
CMNT    
SAMP    
SFOR    
STAG    C
EXPT    CW
OXS1    IADC
AXS1    ETIM
AXS2    B0VL
AXS3    
A2RS    20
A2CT    0.3516
A2SW    0.003
MWFQ    9.851604e+09
MWPW    0.0006325
AVGS    1
SPTP    0.005
RCAG    40
RCHM    1
B0MA    1e-05
B0MF    100000
RCPH    0.0
RCOF    0.0
A1RS    2000
A1SW    10
RCTC    1e-05
*
************************************************************
*
#DSL	1.0 * DEVICE SPECIFIC LAYER
*

.DVC     acqStart, 1.0


.DVC     fieldCtrl, 1.0

AllegroMode        True
Delay              0.0 s
FieldFlyback       On
FieldWait          Wait LED off
GFactor            2.000000
MeasuringHall      False
NbPoints           20
RampCenter         3516.00 G
RampData            G
RampWidth          30.0 G
SetToSampleG       False
StaticField        3501.000 G
StaticFieldMon     3501.000 G
SweepDirection     Up
WidthTM            200.0 G

.DVC     freqCounter, 1.0

FrequencyMon       9.851604 GHz
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
ReplaceMode        On
SmoothMode         Manual
SmoothPoints       1

.DVC     signalChannel, 1.0

AFCTrap            True
AllegroMode        True
AllowShortCt       False
Calibrated         True
ConvFact           9.271e-09
ConvTime           5.00 ms
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
Offset             0.0 %
PolyCof            {2;3,9;0} 0,0.99652,0,0,0.00737177,0,0,-0.00559614,0,0,-2.88221e-05,0,0,1.00404e-05,0,0,3.43695e-08,0,0,-5.0404e-09,0,0,-1.4783e-11,0,0,-1.29132e-12,0
ResCenter          62.5 mm
ResLength          40 mm
Resolution         2000
Resonator          1
SctNorm            True
SctRevision        Allegro
SpuExtension       False
SweepTime          10.00 s
TimeConst          0.01 ms
TimeExp            True
TuneCaps           38

*
************************************************************
