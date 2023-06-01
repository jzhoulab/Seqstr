# SeqStr Documentation

SeqStr is a tool for translating string input into actual sequences. It provides a simple, consolidated way to parse many types of sequence string inputs and convert them into DNA sequence data that can be used for downstream bioinformatics analysis. SeqStr standardizes various patterns of inputs and accepts genome coordinates, mutation and raw sequence nucleotides. It is flexible in parsing many sections of string inputs together into a single coherent output sequence. SeqStr can also render multiple sequences outputs for downstream comparisons.  

1. genomic interval

SeqStr can extract the corresponding genomic sequences by simply providing a genome ID, genomic interval and strand. For example, `[hg38]chr7:5530575-5530625 -` would extract reverse strand of bases 5530575 through 5530625 from chromosome 7 of the hg38 human genome assembly.
  - [reference_genome]chromosome:coordinate-coordinate strand

    Example: `[hg38]chr7:5530575-5530625 -`

      - SeqStr parses `[]` as reference genome, need to load specific assembly files if not default hg38
      - chromosome follows the namespace from the provided assembly files
      - starting and ending coordinates are connected via `-`
      - strand only takes `+` and `-`


2. multiple subsequences

SeqStr can compose multiple subsequences, connected by `;`. Each subsequence can be either a genomic interval (For example, `[hg38]chr7:5530575-5530625 -`) or a raw sequence (For example, `TTAAccggGGNaa`). Subsequence of genomic interval can be modified by a mutation specified with the syntax `@chromosome coordinate reference_alleles alternative_alleles`

  - [reference_genome]chromosome:coordinate-coordinate strand,@chromosome coordinate reference_alleles alternative_alleles;raw sequence; 

    Example: `[hg38]chr7:5530575-5530625 -,@chr7 5530575 C T,@chr7 5530576 GC A;TTAAccggGGNaa;[hg38]chrX:1000000-1000017 +;TTAA;`
    
      - `;` is used to separate multiple sections of sequences. The final outcome consists of all sections and follows the order of input string
      - raw sequence strings are also allowed and remain as they were in the entire output sequence
      - variant format: separate the base sequence and variants specification via `,`
      - variants specification starts with `@`chromosome, then at particular coordinate, change from reference_alleles to alternative_alleles

3. multiple sequences

SeqStr supports multiple sequences separated by `\n` or line breaks and labeling via `<>` embedding the names assigned to each sequence. For example, `<s1>[hg38]chr7:5480600-5580600 -\n<s2>[hg38]chr7:44746680-44846680 +` would be parsed into an array of sequences, with `s1` and `s2` as their names.

 
  - <sequence_name>sequence\n<sequence_name>sequence

    Example: `<s1>[hg38]chr7:5480600-5580600 -\n[hg38]chr7:44746680-44846680 +`

      - SeqStr parses `\n` or line break as delimiter of string input for each single sequence
      - String enclosed by `<>` is treated as the label for the single sequence. If not provided, SeqStr assigns `Sequence i` to the label as default where `i` refers to the index, i.e. ith sequence among all
    
    
