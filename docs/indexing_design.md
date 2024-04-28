# How to index documents

## Parse doc to text

Parse doc base on doc type

## Build inverted index
- Split to tokens, base on space, uppercase character that after a lowercase character -> May have some corner case like: MySQL, VueJS, ...  
- Convert all to lower case
- Correct spelling error by looking up on language dictionaries, check distance between words -> Improving performance ideas: check with only same length words, generate candidates for each word, ...
- Build inverted index base on normalized text
