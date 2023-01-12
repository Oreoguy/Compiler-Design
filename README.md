Bottom Up parsing using LALR 
   
   The bottom-up parsing method constructs the node in the syntax tree in post-order: the top of a subtree is constructed after all of its lower nodes have been constructed. When a bottom-up parser constructs a node, all its children have already been constructed and are present and known. 

    An LALR parser or Look-Ahead LR parser is a simplified version of a Canonical LR parser

    This tool takes LR(0) grammar as input and produces a LALR parsing table. Then any expression can be checked
    against the given grammar
    
    This tool displays following attributes of given BNF grammar :
        1. Terminals and Non Terminals
        2. First
        3. LR(1) states
        4. LALR parser
        5. Parsing Table
        6. Bottom Up parsing step wise

