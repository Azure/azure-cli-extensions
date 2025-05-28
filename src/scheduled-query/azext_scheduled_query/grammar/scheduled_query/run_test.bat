echo off
echo Testing ScheduleQueryCondition
call antlr ScheduleQueryCondition.g4
call javac Schedule*.java
call grun ScheduleQueryCondition expression test.txt -gui
