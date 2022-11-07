  if git diff --exit-code data.csv; then
    echo changes_exist=false
    export changes_exist=false
  else
    echo changes_exist=true
    export changes_exist=true
  fi