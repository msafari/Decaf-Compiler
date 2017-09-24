# Decaf-Compiler

This is a working compiler for Decaf programming language, an object oriented programming language similar to Java but simpler.

Please refer to the following document for more information about decaf language and its lexical and semantic rules: https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-035-computer-language-engineering-spring-2010/projects/MIT6_035S10_decaf.pdf

 ### Usage
* Run `src/decafc.py` with the input Decaf program as the first argument
    it will run for both file_name and file_name.decaf
* Note: you can find some sample decaf test files under `tests/` directory

--------------------------------------
### Major Dependencies
* #### PLY:
  PLY is a 100% Python implementation of the common parsing tools lex
and yacc developed by David Beazley. For more information and download please see http://www.dabeaz.com/ply/


--------------------------------------
 ### HOW IT WORKS

- codegen.py will compile test input file to machine readable code.
You can see some sample generated files in `tests/` directory with `.ami` extension. These are generated files and shouldn't be modified.

- abstratc syntax tree: You can see all ast definitions under `src/ast/`
 more detailed explanation to come soon.
