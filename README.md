# Seqstr Documentation

Seqstr (pronounced as seq-string) is a lightweight tool to compile simple string input into long genomic sequences. It is designed to provide a concise and flexible way to specify long genomic sequences that can be used for downstream analysis. For example, it can be used by web servers to avoid transferring long genomic sequences. Seqstr is also a format specification, which can be implemented in different languages. We also provide a test suite for verifying an implementation.

Seqstr allows using a combination of genome interval coordinates, raw sequence nucleotides, and specifying mutations. A single sequence can be flexibly composed by concatenating multiple subsequences (for example, `[hg38]chr7:5530575-5530625 -, @chr7 5530575 C T, @chr7 5530576 GC A;TTAAccggGGNaa;[hg38]chrX:1000000-1000017 +;TTAA;`). Seqstr can also be used to express multiple named sequences for downstream applications.  


## Contents

- [Seqstr format](#Seqstr-format)
- [Output format](#Output-format)
- [Symbols and terms](#Symbols-and-terms)
- [Python implementation usage](#Python-implementation-usage)

## Seqstr format
### Genomic interval

Use `[reference_genome]chr:start-end strand` to specify an genomic interval. For example, `[hg38]chr7:5530575-5530625 -` would extract cooridnate 5530575 through 5530625 from chromosome 7 of the hg38 reference genome, and take reverse complement of the sequence. 

- `[]` is used to specify the reference genome (UCSC convention), if not specified, the default is hg38.
- chromosome name should be one of the chromosome names from the specified reference genome (UCSC convention), followed by `:`
- start and end coordinates are 0-based, connected via `-`, inclusive for the start coordinate and exclusive for the end coordinate
- strand only takes `+` and `-`, default is `+`. strand is separated from end coordinate by a space

### Composing and modifying sequences

For more flexibly specifying a sequence that is different from the reference genome sequence, Seqstr can take input like `[hg38]chr7:5530575-5530625 -, @chr7 5530575 C T, @chr7 5530576 GC A;TTAAccggGGNaa;[hg38]chrX:1000000-1000017 +;TTAA;`, which is explained below:

#### Compose subsequences

Seqstr can concatenate multiple subsequences connected by `;`. Each subsequence can be either a genomic interval (For example, `[hg38]chr7:5530575-5530625 -`) or a sequence (For example, `TTAAccggGGNaa`). For directly specifying sequence in Seqstr, any characters, e.g. special marking, are allowed and will be included in the output sequence. Because the purpose of Seqstr is to shorten the input size, direct sequence specification is usually used when concatenating with an genomic interval.
- `;` is used to separate multiple sections of sequences. The final outcome consists of all sections and follows the order of input string
- raw sequence strings are also allowed and remain as they were in the entire output sequence

#### Sequence modifier
Any genomic interval can be modified by a mutation or variant specified with the syntax `@chr position reference_allele alternative_allele`. Multiple modifier can be provided to introduce multiple mutations into the same sequence. Mutation specification is with respect to *original sequence coordinates and `+` strand*.

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
    
## Output format

The python CLI outputs sequences in fasta format.

The python API outputs a list of SeqOutput objects `list of (sequence name, sequence, error message)`. For example, `<s1>[hg38]chr7:5480600-5480620 -\n<s2>[hg38]chr7:44746680-44746700 +` returns

```
SeqOutputList = [SeqOutput(Name='s1', Seq='TTGCACTCCAGCCTGGACAA', errormsg=''), SeqOutput(Name='s2', Seq='CCTGGGATGCTTGGCGTGGC', errormsg='')]
```
You can access sequence name, sequence, error message as follows,

```
SeqOutputList[0].Name, SeqOutputList[0].Seq, SeqOutputList[0].errormsg
```

We expect the Seqstr output to be an ordered list that can be accessed with an index. Each element contains a name and a sequence.

## Symbols and terms

- Sequence : complete individual sequence for downstream analysis, consisting of consecutive nucleotides 
- Subsequences : a segment of a sequence; the minimal unit of Seqstr
- Sequence modifier : introduce mutation to the sequence specified by a genomic region
- `[]` : specify the reference genome (UCSC convention)
- `:` : separate chromosome and coordinate
- `-` : means "from...to..." between two valid coordinates (0-based), or "reverse strand" in strand specification
- `+` : "forward strand" in strand specification
- `;` : separate multiple subsequences
- `@` : initiate mutation specification
- `,` : separate mutation specification
- `\n` : separate multiple sequences
- `<>` : enclose the name for sequence

## Python implementation usage

### Installation 

```
pip install seqstr
```

Or 

```
conda install -c bioconda seqstr
```

### CLI Usage

For command line usage, simply provides the Seqstr input file path, `input_file`, to `seqstr.py`, sequences are retrieved and saved in fasta format. `--download` option specifies the genome files to download so that sequences will be retrieved locally in future use. If you only want to download human genome files without retrieval of any sequences, you may run for example, `python seqstr.py --download hg38` without providing `input_file`. If local genome files are not found, `seqstr.py` will query UCSC API instead. `--dir` sets the directory for downloading genome files and the default directory is your working directory. During installation, you may also set the directory which will be stored in `~/.seqstr.config`, and it will be overwritten every time `--dir` is specified. `--output` option is for the output fasta file path and name. The default is saving to `input_file`.fasta in the current working directory.

```
seqstr [-h] [--download DOWNLOAD] [--dir DIR] [--output OUTPUT] input_file
```
Or
```
python seqstr.py [-h] [--download DOWNLOAD] [--dir DIR] [--output OUTPUT] input_file
```

-  -h, --help           show this help message and exit
-  --download DOWNLOAD  Specify the genome files to download
-  --dir DIR            Specify the directory for downloading genome files
-  --output OUTPUT      Specify the output fasta file path and name
-  input_file           Specify the input file

### API Usage

```
from seqstr import seqstr
SeqString = "<s1>[hg38]chr7:5480600-5480620 -\n<s2>[hg38]chr7:44746680-44746700 +"
SeqOutputList = seqstr(SeqString)
for item in SeqOutputList:
 name, seq, errormsg = item.Name, item.Seq, item.errormsg
```

### Test 

- `test.txt.fasta` is generated after running the following command in terminal
```
seqstr test.txt
```
- `test passes` with or without specific error messages are printed to stdout after running test script, `test.py`
```
python test.py
``` 
