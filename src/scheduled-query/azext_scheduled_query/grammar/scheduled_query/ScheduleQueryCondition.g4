/* PARSER RULES */

grammar ScheduleQueryCondition ;

/* Main Rules */

expression          : aggregation (metric_with_quote comes_from)? query_with_quote WHITESPACE operator threshold (WHITESPACE resource_column)? (WHITESPACE dimensions)* (WHITESPACE falling_period)? NEWLINE* ;

aggregation         : WORD WHITESPACE ;

comes_from          : COMESFROM WHITESPACE ;

namespace           : (WORD | '/' | '.')+;

metric_with_quote   : (QUOTE metric QUOTE | metric) WHITESPACE ;

metric              : (WORD | WHITESPACE | '.' | '/' | '_' | '\\' | ':' | '%' | '-' | ',' | '|')+;

query_with_quote    : QUOTE query QUOTE ;

query               : (WORD | WHITESPACE | OPERATOR | AND | OR | where | '&' |'.' | '/' | '('| ')' | '_' | '\\' | ':' | '%' | '-' | ',' | '|' | '==' | '\\"' | '\\\'')+ ;

operator            : OPERATOR WHITESPACE ;

threshold           : NUMBER ;

/* Resource Column */

resource_column     : resource column resource_id ;

resource_id         : (WORD | WHITESPACE | '.' | '/' | '_' | '\\' | ':' | '%' | '-' | ',' | '|')+;

resource            : RESOURCE WHITESPACE ;

column              : COLUMN WHITESPACE ;

/* Falling Period */

falling_period      : at least min_times out of evaluation_period ;

at                  : AT WHITESPACE ;

least               : LEAST WHITESPACE ;

out                 : OUT WHITESPACE ;

of                  : OF WHITESPACE ;

min_times           : NUMBER WHITESPACE ;

evaluation_period   : NUMBER ;

/* Dimensions */

where               : WHERE WHITESPACE ;

dimensions          : where dimension (dim_separator dimension)* ;

dimension           : dim_name dim_operator dim_values ;

dim_separator       : (AND | ',') WHITESPACE ;

dim_operator        : (INCLUDES | EXCLUDES) WHITESPACE ;

dim_val_separator   : (OR | ',') WHITESPACE ;

dim_name            : WORD WHITESPACE ;

dim_values          : dim_value (dim_val_separator dim_value)* ;

dim_value           : (NUMBER | WORD | '-' | '.' | '*' | WHITESPACE | ':'| '~' | ',' | '|' | '%' | '_')+ ;

/* LEXER RULES */

fragment A          : ('a'|'A') ;
fragment C          : ('c'|'C') ;
fragment D          : ('d'|'D') ;
fragment E          : ('e'|'E') ;
fragment F          : ('f'|'F') ;
fragment H          : ('h'|'H') ;
fragment I          : ('i'|'I') ;
fragment L          : ('l'|'L') ;
fragment M          : ('m'|'M') ;
fragment N          : ('n'|'N') ;
fragment O          : ('o'|'O') ;
fragment R          : ('r'|'R') ;
fragment S          : ('s'|'S') ;
fragment U          : ('u'|'U') ;
fragment W          : ('w'|'W') ;
fragment X          : ('x'|'X') ;
fragment T          : ('t'|'T') ;

fragment DIGIT      : [0-9] ;
fragment LOWERCASE  : [a-z] ;
fragment UPPERCASE  : [A-Z] ;

WHERE               : W H E R E ;
COMESFROM           : F R O M ;
RESOURCE            : R E S O U R C E ;
COLUMN              : I D ;
AT                  : A T ;
LEAST               : L E A S T ;
OUT                 : O U T ;
OF                  : O F ;
AND                 : A N D ;
INCLUDES            : I N C L U D E S ;
EXCLUDES            : E X C L U D E S ;
OR                  : O R ;

OPERATOR            : ('<' | '<=' | '=' | '>=' | '>' | '!=') ;
NUMBER              : DIGIT+ ([.,] DIGIT+)? ;
QUOTE               : ('\'' | '"') ;
WHITESPACE          : (' ' | '\t')+ ;
NEWLINE             : ('\r'? '\n' | '\r')+ ;
WORD                : (LOWERCASE | UPPERCASE | DIGIT | '_')+ ;

