The program uses a custom made software solution for task scheduling
with a good plugin support. A task works towards a goal and that goal
will ultimately earn points.

`Goal = (goal_id, points)`

Several tasks can work toward the same goal and each task specifies
how many points it provides towards it's goal. The software provides
some basic primitives for evaluating value expressions so for example
the number of points for a program could be the expression

`max(1, 4 * 5, 20 + 1)`

The program also provides conditions for tasks to be met. A task is
met by default (as it not being met would not be a sensible default,
it would essentially be void) but can also evaluate a boolean
expression to see if it is fulfilled. An example boolean expression
could be

`((14 - 12) > (14 / 7)) or (13 == 15)`

Tasks are described using JSON, so the above two expressions would be

```
{
  "MAX": [
    1,
    {"*": [4, 5] },
    {"+": [20, 1] }
  ]
}
```


and

```
{
  "OR": [
    { ">": {
      "lhs": {"-": [14, 12]},
      "rhs": {"/": [14, 7]}
    }},
    { "=" : [13, 15]}
  ]
}
```

For each keyword there is a corresponding function and it will be
looked up at runtime what that function is. By adding plugins to the
context that runs the resolution we will evaluate the JSON with custom
functionality. During the resolution step the context will go through
all plugins and use the latest registered one that says it can handle
a that keyword. For example we implement "session" and "uppgift" in
the aaps plugin that can then handle "session" and "uppgift" keywords.



