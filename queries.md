# Useful queries

These queries uses the following tools:
* `jq` 

### Keys with card and code

Get all tags (keys) with codes.

```shell
jq '.[].keys[] | select((.code != "") and (.card != "")) | {id,code}' customer_dump.json | jq -s
```

### Customers of format nn-nnn

Get all customers with name nn-nnn.

```shell
jq 'map(select(.details.name | test("^[0-9][0-9]-[0-9][0-9][0-9]")?))' customer_dump.json
```
