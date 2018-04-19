$Type
"cmd|raw|lin|pow|exp|log|poly|enum|mask|date|text|func"

$Color
{ $red:   Number, //int
  $green: Number, //int
  $blue:  Number, //int
  $alpha: Number }//int

$Datetime
{ $date: Number, //int
  $time: Number }//float
  
$Period
{ $period: Number }//float

$Level
[ { $name: String,
    $color: Object,//$Color
    $value: Number,//int
    ... },
  { ... },//Level:null
  { ...,//Level:int
    $lower: Number,  //int
    $upper: Number },//int
  { ...,//Level:float
    $lower: Number,  //float
    $upper: Number },//float
  { ...,//Level:date
    $lower: Object,  //$Period
    $upper: Object },//$Period
  { ...,//Level:map
    $keys: [ Number, ... ] } ]//int
       
$Packet
{ $data: [ Number, ... ] }//int

$Command
{ $key: Number,//int
  $values: [ 
    Number | String | Object,//$Datetime
    ...
  ] }

$Telemetry
{ $key: Number,//int
  $value: Number | String | Object,//$Datetime
  $epoch: Object,//$Datetime
  $words: [ String, ... ],
  $color: Object }//$Color

$Mnemonic
[ { $key: Number,//int
    $name: String,
    $size: Number,//int
    $type: String,//$Type
    ... },
  { ...,//$Mnemonic:cmd
    $type: "cmd",
    $conf: [ Number, ... ],//int
    $level: Object },//$Level:str
  { ...,//$Mnemonic:raw
    $type: "raw",
    $config: null,
    $levels: [ Object, ... ] },//$Level:int
  { ...,//$Mnemonic:lin|pow|log
    $type: "lin|pow|log",
    $config: { $lower: Number,  //float
               $upper: Number },//float
    $levels: [ Object, ... ] },//$Level:float
  { ...,//$Mnemonic:exp
    $type: "exp",
    $config: { $base: Number,  //float
               $rate: Number },//float
    $levels: [ Object, ... ] },//$Level:float
  { ...,//$Mnemonic:poly
    $type: "poly",
    $config: [ Number, ... ],//float
    $levels: [ Object, ... ] },//$Level:float
  { ...,//$Mnemonic:enum
    $type: "enum",
    $config: [ { $key: Number,//int
                 $value: String }, ... ],
    $levels: [ Object, ... ] },//$Level:map
  { ...,//$Mnemonic:mask
    $type: "mask",
    $conf: [ { $key: Number,//int
               $value: String }, ... ],
    $levels: [ Object, ... ] },//$Level:map
  { ...,//$Mnemonic:date
    $type: "date",
    $config: { $epoch: Object,  //$Datetime
               $scale: Object },//$Period
    $levels: [ Object, ... ] },//$Level:date
  { ...,//$Mnemonic:text
    $size: null,
    $type: "text",
    $config: { $format: String,
               $keys: [ Number, ... ] },//int
    $level: Object } ,//$Level:null
  { ...,//$Mnemonic:func
    $size: null,
    $type: "calc",
    $config: [ Number, ... ],//int
    $levels: [ Object, ... ] } ]//$Level
