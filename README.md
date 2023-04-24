# SeqStr Documentation

SeqStr translates sequence string input into actual sequences for downstream analysis. Some of the major capabilities include:
  1. Extracting sequences from genomes using selene_sdk. By providing a genome ID and coordinates, the code can extract the corresponding DNA sequence from the genome. For example, [hg38]chr1:100-200 + would extract bases 100 through 200 from chromosome 1 of the hg38 human genome assembly.
  2. Handling mutation strings using `@`. The code can find the position specified after @ and substitute the reference base at that position with the provided alternate base. For example, `[hg38]chr1:100-200 +, @120 A T` would extract that chr1:100-200 sequence but replace base 120 with A, giving AACTGT. 
  3. Concatenating and parsing comma-separated input sections. SeqStr splits on `;` and `,` to parse multiple inputs together. For example, `[hg38]chr1:100-200 +, @120 A T; ACTGN` would extract and mutate the first sequence, then concatenate ACTGN, resulting in AACTGTN.

It accepts the following patterns/formats of string input:

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
