$Datetime
{ $date: Number, //int
  $time: Number }//float
  
$Period
{ $period: Number }//float

$Color
{ $red:   Number, //int
  $green: Number, //int
  $blue:  Number, //int
  $alpha: Number }//int

$Scale
[ { _id: ObjectId,
    $name: String,
    $size: Number,//int
    $type: String,
    ... },
  { ...,//$Scale:raw
    $type: "raw" },
  { ...,//$Scale:lin|pow|log
    $type: "lin|pow|log",
    $lower: Number,  //float
    $upper: Number },//float
  { ...,//$Scale:exp
    $type: "exp",
    $base: Number,  //float
    $rate: Number },//float
  { ...,//$Scale:poly
    $type: "poly",
    $coeff: [ Number, ... ] },//float
  { ...,//$Scale:enum|mask
    $type: "enum|mask",
    $map: [ { $key: Number,//int
              $value: String }, ... ] },
  { ...,//$Scale:date
    $type: "date",
    $epoch: Object,  //$Datetime
    $scale: Object },//$Period
  { ...,//$Scale:func
    $type: "func",
    $script: String,
    $args: [ ObjectId, ... ] } ]//$Mneumonic|tlm._id

$Level
[ { _id: ObjectId,
    $name: String,
    $type: String,
    $color: Object,//$Color
    $value: Number,//int
    ... },
  { ...,//Level:null
    $type: null },
  { ...,//Level:int
    $type: "int",
    $lower: Number,  //int
    $upper: Number },//int
  { ...,//Level:float
    $type: "float",
    $lower: Number,  //float
    $upper: Number },//float
  { ...,//Level:date
    $type: "date",
    $lower: Object,  //$Period
    $upper: Object },//$Period
  { ...,//Level:map
    $type: "map",
    $keys: [ Number, ... ] } ]//int
       
$Packet
{ _id: ObjectId,
  $data: [ Number, ... ] }//int

$Command
{ _id: ObjectId,
  $???: ObjectId,//$Mnemonic:cmd._id
  $epoch: Object,//$Datetime
  $values: [ 
    Number | String | Object,//$Datetime
    ...
  ],
  $words: [ String, ... ],
  $color: Object }//$Color

$Telemetry
{ _id: ObjectId,
  $???: ObjectId,//$Mnemonic:tlm._id
  $epoch: Object,//$Datetime
  $value: Number | String | Object,//$Datetime
  $words: [ String, ... ],
  $color: Object }//$Color

$Table
{ _id: ObjectId,
  $???: ObjectId,//$Mnemonic:table._id
  $head: { 
    Number | String | Object,//$Datetime
    ...
  },
  $body: [ { 
    String: Number | String | Object,//$Datetime
    ... }, ... ],
  $tail: { 
    Number | String | Object,//$Datetime
    ...
  } }

$Mnemonic
[ { _id: ObjectId,
    $name: String,
    $key: Number,//int
    $type: String,
    ... },
  { ...,//$Mnemonic:null
    $key: null,
    $type: null,
    $scale: ObjectId },//$Scale._id
  { ...,//$Mnemonic:cmd
    $type: "cmd",
    $values: [ ObjectId, ... ],//$Mneumonic:null._id
    $level: ObjectId },//$Level:null._id
  { ...,//$Mnemonic:tlm
    $type: "tlm",
    $scale: ObjectId,//$Scale._id
    $levels: [ ObjectId, ... ] },//$Level._id
  { ...,//$Mnemonic:msg
    $type: "msg",
    $format: String,//printf
    $values: [ ObjectId, ... ] },//$Mnemonic._id
    $level: ObjectId } ,//$Level:null._id
  { ...,//$Mnemonic:table
    $type: "table",
    $head: [ ObjectId, ... ],//$Mnemonic._id
    $body: { $rows: Number,//int
             $cols: [ ObjectId, ... ] },//$Mnemonic._id
    $tail: [ ObjectId, ... ] } ]//$Mnemonic._id
