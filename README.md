# GPSeq-Pipeline

## Current errors

Will not run with only two bed files

There is an error in the gpseq-radical.R code

When I try to run it with only two bed files I get the error:

assert(2 <= nrow(bmeta), "Provide at least two bed files.") :                                                                      
  expr is not TRUE

I realized this error is because in line 794 (around there) the line 
`bmeta = data.table::fread(args$bmeta_path)
 assert(2 <= nrow(bmeta), "Provide at least two bed files.")` is treating the first line as a header
 
 To fix this, I added: 
 `bmeta = data.table::fread(args$bmeta_path, header=F)
 assert(2 <= nrow(bmeta), "Provide at least two bed files.")`
 
 Not sure how to fix this in the docker implementation
 
## Overview

There are multiple ways to run the GPSeq pipeline. Specifically, you can either use a docker container (which contains all the necessary packages), or run the commands manually (which requires installation of all the correct packages). 

[Docker instructions](./docker/)

[Manual instructions](./manual) 

Tutorial modified from https://github.com/GG-space/gpseq-preprocessing-tutorial
