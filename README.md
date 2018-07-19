# AT-T Intelx86 converter
Converter between AT&amp;T and Intelx86 syntaxes for assembly and SIMD.

## TODO

- [x] If there are two parameters for an instructions, switch them.
- [x] Split the input into tokens.
- [ ] If there are comments, simply copy them.
- [x] Manage the clobbers.
- [ ] Add a GUI.
- [x] Add tabulations for readability.
- [x] Add ';' add the end of the line.
- [ ] Link to the issues page incase the output is wrong.
- [ ] Use Rest API for issues.
- [ ] When parsing the clobbers, detect comment blocks.
- [ ] Replace the variable names based on the clobbers info.


## Notes

- In AT&amp;T, clobber lines should begin with a ':'.