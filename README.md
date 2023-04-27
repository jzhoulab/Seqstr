# SeqStr Documentation

SeqStr is a tool for translating string input into actual sequences. It provides a simple, consolidated way to parse many types of sequence string inputs and convert them into DNA sequence data that can be used for downstream bioinformatics analysis. SeqStr standardizes various patterns of inputs and accepts genome coordinates, mutation and raw sequence nucleotides. It is flexible in parsing many sections of string inputs together into a single coherent output sequence. SeqStr can also render multiple sequences outputs for downstream comparisons.  

Some of the major capabilities include:
  1. Extracting sequences from genomes. By providing a genome ID and coordinates, the code can extract the corresponding DNA sequence from the genome. For example, [hg38]chr1:100-200 + would extract bases 100 through 200 from chromosome 1 of the hg38 human genome assembly.
  2. Handling mutation strings using `@`. The code can find the position specified after @ and substitute the reference base at that position with the provided alternate base. For example, `[hg38]chr1:100-200 +, @120 A T` would extract that chr1:100-200 sequence but replace base 120 with A, giving AACTGT. 
  3. Concatenating and parsing comma-separated input sections. SeqStr splits on `;` and `,` to parse multiple inputs together. For example, `[hg38]chr1:100-200 +, @120 A T; ACTGN` would extract and mutate the first sequence, then concatenate ACTGN, resulting in AACTGTN.
  4. Supporting multiple sequences separated by `\n` or line breaks and labeling via `<>` embedding the names assigned to each sequence. For example, `<s1>[hg38]chr7:5480600-5580600 -\n<s2>[hg38]chr7:44746680-44846680 +` would be parsed into an array of sequences, with `s1` and `s2` as their labels.

It accepts the following patterns/formats of string input for single sequence (single_SeqStr):

- [reference_genome]chromosome:coordinate-coordinate strand

  Example: `[hg38]chr7:5530575-5530625 -`

    - SeqStr parses `[]` as reference genome, need to load specific assembly files if not default hg38
    - chromosome follows the namespace from the provided assembly files
    - starting and ending coordinates are connected via `-`
    - strand only takes `+` and `-`

- [reference_genome]chromosome:coordinate-coordinate strand;raw sequence;

  Example: `[hg38]chr7:5530590-5530610 -;TTAAccggGGNaa;[hg38]chrX:1000000-1000017 +`

    - consistent with the above specifications
    - `;` is used to separate multiple sections of sequences. The final outcome consists of all sections and follows the order of input string
    - raw sequence strings are also allowed and remain as they were in the entire output sequence

- [reference_genome]chromosome:coordinate-coordinate strand,@chromosome coordinate reference_alleles alternative_alleles 

  Example: `[hg38]chr7:5530575-5530625 -,\n@chr7 5530575 C T,\n@chr7 5530576 GC A`

    - variant format: separate the base sequence and variants specification via `,`, line break is optional
    - variants specification starts with `@`chromosome, then at particular coordinate, change from reference_alleles to alternative_alleles
 
On top of the patterns/formats of string input for single sequence (single_SeqStr), multiple sequences takes the following form of concatenation of single_SeqStr
 
- <sequence_label>single_SeqStr\n<sequence_label>single_SeqStr

  Example: `<s1>[hg38]chr7:5480600-5580600 -\n[hg38]chr7:44746680-44846680 +`

    - SeqStr parses `\n` or line break as delimiter of string input for each single sequence
    - String enclosed by `<>` is treated as the label for the single sequence. If not provided, SeqStr assigns `Sequence i` to the label as default where `i` refers to the index, i.e. ith sequence among all
    
    
