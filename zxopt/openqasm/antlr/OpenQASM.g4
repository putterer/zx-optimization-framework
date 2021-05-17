grammar OpenQASM;
// based on: https://arxiv.org/pdf/1707.03429v2.pdf

mainprogram: version program;
version: 'OPENQASM' REAL ';';

program: statement+;

statement:
    decl
    | gatestmt
    | 'opaque' ID idlist ';'
    | 'opaque' ID '(' ')' idlist ';'
    | 'opaque' ID '(' idlist ')' idlist ';'
    | statementqop
    | conditionalqop
    | barrier;

barrier: 'barrier' anylist ';';

decl: qreg_decl | creg_decl;
qreg_decl: 'qreg' ID '[' NNINTEGER ']' ';';
creg_decl: 'creg' ID '[' NNINTEGER ']' ';';

gatestmt: gatedecl goplist '}' | gatedecl '}';

gatedecl:
    'gate' ID gateqargs '{'
    | 'gate' ID '(' ')' gateqargs '{'
    | 'gate' ID '(' gateparams ')' gateqargs '{';

gateqargs: idlist;
gateparams: idlist;

statementqop: qop;
conditionalqop: 'if' '(' ID '==' NNINTEGER ')' qop;


goplist: (goplistentry)*;
goplistentry: uop | 'barrier' idlist ';';


qop:
    uop
    | measure
    | reset_op;

reset_op: 'reset' argument ';';
measure: 'measure' argument '->' argument ';';


uop:
    'U' '(' explist ')' argument ';'
    | 'CX' argument ',' argument ';'
    | ID anylist ';'
    | ID '(' ')' anylist ';'
    | ID '(' explist ')' anylist ';';



idlist: (ID ',')* ID;
anylist: (argument ',')* argument;
//anylist: idlist | mixedlist;
//mixedlist:
//    ID '[' NNINTEGER ']'
//    | mixedlist ',' ID
//    | mixedlist ',' ID '[' NNINTEGER ']'
//    | idlist ',' ID '[' NNINTEGER ']';

argument: ID | ID '[' NNINTEGER ']';

explist: (exp ',')* exp;
exp:
    REAL| NNINTEGER | PI | ID
    | exp '+' exp | exp '-' exp | exp '*' exp | exp '/' exp
    | exp '^' exp | '-' exp | '(' exp ')' | unaryop '(' exp ')';
unaryop: 'sin' | 'cos' | 'tan' | 'exp' | 'ln' | 'sqrt';

PI: 'pi';
ID: [a-z][A-Za-z0-9_]*;
NNINTEGER: [0-9]+;
REAL: [+-]? NNINTEGER '.' [0-9]+ ([eE][-+]?[0-9]+)?;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;
WHITESPACE:  [ \r\n\t\u000C]+ -> skip;