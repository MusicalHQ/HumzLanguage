# Everything

## Basics

### Misc

* `new_line `
  * Prints a new line character.

### Math

* ` add addr_type var_1 addr_type var_2 addr_type ouput_var `
  * Sets `output_var` to `var_1 + var_2`
* ` sub addr_type var_1 addr_type var_2 addr_type output_var`
  * Sets `ouput_var` to `var_1 - var_2 `
* `mul addr_type var_1 addr_type var_2 addr_type output_var`
  * Sets `ouput_var` to `var_1 * var_2`
* ` div addr_type var_1 addr_type var_2 addr_type output_var`
  * Sets `output_var` to `var_1 / var_2`
* ` mod addr_type var_1 addr_type var_2 addr_type output_var`
  * Sets `output_var` to `var_1 % var_2`
* ` pwr addr_type var_1 addr_type var_2 addr_type output_var`
  * Sets `output_var` to `var_1 ** var_2`

### If statements

* `if addr_type var_1`
  * Does stuff if `var_1 == 0`
* `if_not addr_type var_1`
  * Does stuff if `not var_1 == 0`
* `if_equals addr_type var_1 addr_type var_2`
  * Does stuff if `var_1 == var_2`
* `if_not_equals addr_type var_1 addr_type var_2`
  * Does stuff if `not var_1 == var_2`
* `if_greater addr_type var_1 addr_type var_2`
  * Does stuff if `var_1 > var_2`

## Lists

### Lists

* `list name length`
  * Creates a list called `name` of length `length`.
* `list_set name index type value`
  * Sets the item `index` of list `name` to the value `value` of type `type`.
* `list_read_basic name`
  * Takes user input and sets list `name` to the value of the input.
* `list_out name index type`
  * Outputs the item `index` of list `name` as type `type`.
* `list_set_index name addr_type var_1 type value`
  * Sets the item with index equal to the value of `var_1` of list `name` to the value `value` of type `type`.
* `list_out_index name addr_type var_1 type`
  * Outputs the item with index equal to the value of `var_1` of list `name` as the type `type`.
* `list_get name index addr_type var_1`
  * Sets the value of `var_1` to the item `index` of list `name`.
* `list_get_index name addr_type var_1 addr_type var_2`
  * Sets the value of `var_2` to the item with index equal to the value of `var_1` of list `name`.
* `list_len name addr_type var_1`
  * Sets the value of `var_1` to the length of list `name`.
* `list_cpy name index addr_type var_1`
  * Sets the value of `var_1` to the item `index` of list `name`.
* `list_cpy_index name addr_type var_1 addr_type var_2`
  * Sets the value of `var_2` to the item with index equal to the value of `var_1` of list `name`.
* `out_list name type`
  * Outputs the list `name` as type `type`.

## Reading

### Ints

* `read_int addr_type var_1`
  * Takes an integer as user input and sets `var_1` to the value of user input.


