@ECHO OFF

if not exist .env (
    echo File ".env" does not exist

) else (

    for /f %%l in (.env) do (
        set sVar=%%l

        if not %%l == # (
            set %%l
        )

    )
    echo Environment variables set successfully

)
