# Useful queries

These queries uses the following tools:
* `jq` 

### Keys with card and code

Get all tags (keys) with codes.

```shell
jq '.[].keys[] | select((.code != "") and (.card != "")) | {id,code}' customer_dump.json | jq -s
```
