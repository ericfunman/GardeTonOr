@echo off
echo =====================================
echo TEST OPENAI BILLING API
echo =====================================
echo.

call venv\Scripts\activate.bat

python test_openai_billing.py

echo.
echo =====================================
echo Appuyez sur une touche pour fermer
pause > nul
