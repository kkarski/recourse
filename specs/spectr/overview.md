```yaml
spectr:
  - conf:
      - a: setup the role of the client
  - init: initialize basic folder structure for spectr
  - plan:
      - create phased execution plan of each acceptance criteria and test case
  - export:
      - f: json, markdown
  - uc:
      - add:
          - t: use case title
      - read:
          - id: read the use case title and description by case id
      - list: list use cases
      - update:
          - id: id of use case to update
          - t: updated title text
      - delete:
          - id: id of use case to delete
  - ac:
      - add:
          - desc: text of acceptance criteria to add
      - read:
          - id: id of acceptance criteria to read
      - delete:
          - id: id of acceptance criteria to delete
      - update:
          - id: id of acceptance criteria to update
          - desc:
      - list:
          - r: list acceptance recursively
  - test:
      - add: add a test case
      - update:
          - id: id of test case to update
      - read:
          - id: id of test case to read
      - delete:
          - id: id of test case to delete
  - qs:
      - ask:
          - a: author role
          - t: target role
          - id: id of entity to ask question about (can be ac*, uc*, spec*)
      - answer:
          - a: author role
          - id: id of question
      - list
  - feedback:
      - add

```

```xml

<spectr>

</spectr>
```