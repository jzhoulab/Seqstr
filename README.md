# Seqstr Documentation

Seqstr (pronounced as seq-string) is a lightweight tool to compiles string input into genomic sequences. It is designed to provide a simple and flexible way to specify long genomic sequence that can be used for downstream analysis. Seqstr allows using a combination of genome interval coordinates, raw sequence nucleotides and allows specifying mutations. It is flexible in parsing many sections of string inputs together into a single coherent output sequence. Seqstr can also render multiple sequences outputs for downstream comparisons.  

Seqstr is also a format specification, which can be implemented in different languages. We will soon provide a test suite for verifying an implementation.

### Basic usage

Use `[reference_genome]chr:start-end strand` to specify an genomic interval. For example, `[hg38]chr7:5530575-5530625 -` would extract cooridnate 5530575 through 5530625 from chromosome 7 of the hg38 reference genome, and take reverse complement of the sequence. 

- `[]` is used to specifcy the reference genome (UCSC convention), if not specified, the default is hg38.
- chromosome name should be one of the chromosome names from the specified reference genome (UCSC convention), followed by `:`
- start and end coordinates are 0-based, connected via `-`, inclusive for the start coordinate and exclusive for the end coordinate
- strand only takes `+` and `-`, default is `+`. strand is separated from end coordinate by a space

For more flexibly specifying a sequence that is different from the reference genome sequence, Seqstr can take input like `[hg38]chr7:5530575-5530625 -, @chr7 5530575 C T, @chr7 5530576 GC A;TTAAccggGGNaa;[hg38]chrX:1000000-1000017 +;TTAA;`, which is explained below:

#### Compose subsequences

Seqstr can concatenate multiple subsequences connected by `;`. Each subsequence can be either a genomic interval (For example, `[hg38]chr7:5530575-5530625 -`) or a sequence (For example, `TTAAccggGGNaa`). For directly specifying sequence in Seqstr, any characters are allowed and will be included in the output sequence. Because the purpose of Seqstr is to shorten the input size, direct sequence specification is usually used when concatenating with an genomic interval.
- `;` is used to separate multiple sections of sequences. The final outcome consists of all sections and follows the order of input string
- raw sequence strings are also allowed and remain as they were in the entire output sequence

#### Sequence modifier
Any genomic interval can be modified by a mutation or variant specified with the syntax `@chr position reference_allele alternative_allele`. Multiple modifier can be provided to introduce multiple mutations into the same sequence. 

- mutation specification is separated from the genomic interval specification by `,` 
- mutation specification starts with `@`chromosome, then at particular coordinate, change from reference_allele to alternative_allele
- multiple mutations are allowed and separated by `,`. we note that while any mutation may change the length of the sequence, all mutation coordinates are relative to the original reference genome sequence. 
- Overlapping mutations are not allowed.
 

### Multiple sequences

Seqstr supports specifying multiple sequences separated by `\n` or line breaks and labeling each sequence via `<>` embedding the names assigned to each sequence. For example, 
```
<s1>[hg38]chr7:5480600-5580600 -
<s2>[hg38]chr7:44746680-44846680 +
``` 
would be parsed into an array of sequences, with `s1` and `s2` as their names.
- Seqstr interprets `\n` or line break as separator for multiple sequences
- String enclosed by `<>` at the beginning of a sequence is used as the name for the single sequence. If not provided, Seqstr assigns `i` to the name by default where `i` refers to the numerical order of the sequence starting from 0.
    
### Output format

In the python implementation, Seqstr outputs a tuple of `(list of (sequence name, sequence), error message)`. For example, `<s1>[hg38]chr7:5480600-5480620 -\n<s2>[hg38]chr7:44746680-44746700 +` returns

```
([('s1', 'TTGCACTCCAGCCTGGACAA'), ('s2', 'CCTGGGATGCTTGGCGTGGC')], '')
```
Generally, we expect the Seqstr output to be a lists that can be access with an index and each element contains a name and the a sequence which can also be accessed by an index.
