# filter fields
jq '.data | to_entries[] | {name: .key, manaValue: .value[0].manaValue}' AtomicCards.json > AtomicCards.filtered.json   