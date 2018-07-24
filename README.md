# AT-T Intelx86 converter
Converter between AT&amp;T and Intelx86 syntaxes for assembly and SIMD.

## TODO

- [x] If there are two parameters for an instructions, switch them.
- [x] Split the input into tokens.
- [x] If there are comments, simply copy them.
- [x] Manage the clobbers.
- [x] Add a GUI.
- [x] Add tabulations for readability.
- [x] Add ';' add the end of the line.
- [ ] Link to the issues page in case the output is wrong.
- [ ] Use Rest API for issues.
- [ ] When parsing the clobbers, detect comment blocks.
- [x] Replace the variable names based on the clobbers info.
- [x] Manage offsets
- [x] Manage comments sticked with the argument.
- [x] To ATT: Substract the set of labels from the set of variables.
- [ ] To ATT: Manage instructions with a single argument.
- [ ] Pre-fill gui based on cli arguments.
- [x] Add cli argument for no-gui execution.
- [ ] Add 'clear' button.
- [ ] Add a title and an icon to the window.
- [ ] Scale boxes with window.


## Notes

### AT&T syntax

- Clobber lines should begin with a ':'.


### Intel syntax

- Lines should end with ';', except labels.