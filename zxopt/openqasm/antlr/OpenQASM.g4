grammar OpenQASM;
// based on: https://arxiv.org/pdf/1707.03429v2.pdf

mainprogram: version program;
version: 'OPENQASM' REAL ';';

program: statement+;

statement:
    decl
    | gatedecl goplist '}'
    | gatedecl '}'
    | 'opaque' ID idlist ';'
    | 'opaque' ID '(' ')' idlist ';'
    | 'opaque' ID '(' idlist ')' idlist ';'
    | qop
    | 'if' '(' ID '==' NNINTEGER ')' qop
    | 'barrier' anylist ';';

decl: qreg_decl | creg_decl;
qreg_decl: 'qreg' ID '[' NNINTEGER ']' ';';
creg_decl: 'creg' ID '[' NNINTEGER ']' ';';

gatedecl:
    'gate' ID idlist '{'
    | 'gate' ID '(' ')' idlist '{'
    | 'gate' ID '(' idlist ')' idlist '{';

goplist:
    (uop | 'barrier' idlist ';')*;

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



anylist: idlist | mixedlist;
idlist: (ID ',')* ID;
mixedlist:
    ID '[' NNINTEGER ']'
    | mixedlist ',' ID
    | mixedlist ',' ID '[' NNINTEGER ']'
    | idlist ',' ID '[' NNINTEGER ']';

argument: ID | ID '[' NNINTEGER ']';

explist: (exp ',')* exp;
exp:
    REAL| NNINTEGER | 'pi' | ID
    | exp '+' exp | exp '-' exp | exp '*' exp | exp '/' exp
    | exp '^' exp | '-' exp | '(' exp ')' | unaryop '(' exp ')';
unaryop: 'sin' | 'cos' | 'tan' | 'exp' | 'ln' | 'sqrt';


ID: [a-z][A-Za-z0-9_]*;
NNINTEGER: [0-9]+;
REAL: [+-]? NNINTEGER '.' [0-9]+ ([eE][-+]?[0-9]+)?;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;
WHITESPACE:  [ \r\n\t\u000C]+ -> skip;