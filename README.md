# SeqStr Documentation

SeqStr translates sequence string input into actual sequences for downstream analysis. It accepts the following patterns/formats of string input:

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
