IF NOT DEFINED PYTHONPATH (
  FOR /f "delims=" %%p in ('where python') do SET PYTHONPATH=%%p
)

START "Qt Designer" "%PYTHONPATH:~0,-11%\Lib\site-packages\qt6_applications\Qt\bin\designer.exe" "%~d0%~p0..\res\design.ui" "%~d0%~p0..\res\about.ui" "%~d0%~p0..\res\update_checker.ui"
