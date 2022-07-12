@ECHO OFF

IF NOT DEFINED PYTHONPATH (
  setlocal EnableDelayedExpansion

  SET n=0
  FOR /f "delims=" %%p in ('where python') do (
    SET pythonFiles[!n!]=%%p
    SET /A n+=1
  )
  SET PYTHONPATH=!pythonFiles[0]!
)

START "Qt Designer" "%PYTHONPATH:~0,-11%\Lib\site-packages\qt6_applications\Qt\bin\designer.exe"^
 "%~d0%~p0..\res\design.ui"^
 "%~d0%~p0..\res\about.ui"^
 "%~d0%~p0..\res\settings.ui"^
 "%~d0%~p0..\res\update_checker.ui"
