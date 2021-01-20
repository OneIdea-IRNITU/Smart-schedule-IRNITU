@ECHO OFF

for /f %%l in (.env.example) do (
    set sVar=%%l

    if not %%l == # (
        set %%l
    )
)
echo Environment variables set successfully


