import pyfaidx
import re
import requests
import sys
import os
import subprocess
import argparse


class baseSeq:
    def __init__(self, Seq, Chr, Start, Strand, errormsg):
        self.Seq = Seq
        self.Chr = Chr
        self.Start = Start
        self.Strand = Strand
        self.errormsg = errormsg


class SeqOutput:
    def __init__(self, Name, Seq, errormsg):
        self.Name = Name
        self.Seq = Seq
        self.errormsg = errormsg


def to_fasta(SeqOutput, filepath):
    with open(filepath, "w") as file:
        for item in SeqOutput:
            if item.errormsg == "":
                file.write(f">{item.Name}\n")
                seq = item.Seq
                seq_br = '\n'.join([seq[i:i+80] for i in range(0, len(seq), 80)])
                file.write(f"{seq_br}\n")
            else:
                print(item.Name, " Error:", item.errormsg)


def get_genome_dir():
    config_file_path = os.path.expanduser("~/.seqstr.config")
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            for line in config_file:
                if line.startswith("GENOME_DIR="):
                    GENOME_DIR = line.split("=")[1].strip()
                    break
    else:
        GENOME_DIR = os.getcwd()

    return GENOME_DIR


def download(par):
    url = (
        "https://hgdownload.soe.ucsc.edu/goldenPath/"
        + par
        + "/bigZips/"
        + par
        + ".fa.gz"
    )
    output_file = par + ".fa.gz"
    # Download the file using wget
    download_command = ["wget", url, "-O", output_file]
    try:
        subprocess.run(download_command, check=True)
        print("Download completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Download failed")
    # Extract the downloaded file using gunzip
    extract_command = ["gunzip", output_file]
    try:
        subprocess.run(extract_command, check=True)
        print("Extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Extraction failed")


def reverse_seq(seq):
    rev_seq = ""
    dct = {
        "A": "T",
        "C": "G",
        "G": "C",
        "N": "N",
        "T": "A",
        "a": "T",
        "c": "G",
        "g": "C",
        "n": "N",
        "t": "A",
    }
    for item in seq:
        if item in dct.keys():
            rev_seq += dct[item]
        else:
            rev_seq += item
    return rev_seq[::-1]


def extract_baseseq(text):
    text = text.strip()
    # chr:start-end strand
    if ":" in text:
        try:
            geno = text[
                re.search("\[", text).start() + 1 : re.search("\]", text).start()
            ]
            sub = text[re.search("\]", text).start() + 1 :].split(":")
        except:
            geno = "hg38"
            sub = text.lstrip().split(":")
        chr = sub[0]
        position = sub[1].split(" ")[0].replace(" ", "")
        try:
            start = int(position.split("-")[0])
            end = int(position.split("-")[1])
        except:
            return baseSeq(None, None, None, None, "invalid coordinate input")
        try:
            strand = sub[1].split(" ")[1]
            if strand not in ["+", "-"]:
                return baseSeq(None, None, None, None, "invalid strand input")
        except:
            return baseSeq(None, None, None, None, "invalid strand input")
        # define genome input path using dict map
        GENOME_DIR = get_genome_dir()
        if os.path.exists(GENOME_DIR + geno + ".fa"):
            genome = pyfaidx.Fasta(GENOME_DIR + geno + ".fa")
            try:
                seq = str(genome[chr][start:end]).upper()
                if len(seq) < 1:
                    return baseSeq(
                        None, None, None, None, "cannot retrieve sequence from pyfaidx"
                    )
            except:
                return baseSeq(
                    None, None, None, None, "cannot retrieve sequence from pyfaidx"
                )
        else:
            url = "https://api.genome.ucsc.edu/getData/sequence?"
            params = {"genome": geno, "chrom": chr, "start": start, "end": end}
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    seq = response.json().get("dna").upper()
                else:
                    return baseSeq(
                        None, None, None, None, "cannot retrieve sequence from UCSC API"
                    )
            except requests.RequestException as e:
                return baseSeq(
                    None, None, None, None, "cannot retrieve sequence from UCSC API"
                )
        return baseSeq(seq, chr, start, strand, "")
    else:
        return baseSeq(text.upper(), None, None, None, "")


def seqstr(text):
    # sec for arr, sub for string
    # each section ends with ;
    # , for continuation
    # @chr mutpos ref alt
    # \n for multiple sequences
    def singleseqstr(SeqName, sub0text):
        output = ""
        # remove extra spaces
        sub0text = re.sub(" +", " ", sub0text)
        sec1 = sub0text.split(";")
        for sub1 in sec1:
            # remove extra spaces
            sub1 = re.sub(" +", " ", sub1)
            if "," in sub1:
                sec2 = sub1.split(",")
                # base seq
                bSeq = extract_baseseq(sec2[0])
                baseSeq, baseSeqChr, baseSeqStart, baseSeqStrand, errormsg = (
                    bSeq.Seq,
                    bSeq.Chr,
                    bSeq.Start,
                    bSeq.Strand,
                    bSeq.errormsg,
                )
                if errormsg != "":
                    return SeqOutput(SeqName, None, errormsg)
                variation = []
                for sub2 in sec2:
                    # check overlap then chop by affected region
                    if "@" in sub2:
                        sec3 = sub2[re.search("@", sub2).start() + 1 :].split(" ")
                        try:
                            mutpos = int(sec3[1]) - baseSeqStart
                        except:
                            return SeqOutput(
                                SeqName, None, "invalid variant coordinate"
                            )
                        try:
                            ref = sec3[2].upper()
                            alt = sec3[3].upper()
                        except:
                            return SeqOutput(
                                SeqName, None, "invalid reference/alternative allele"
                            )
                        variation.append((mutpos, mutpos + len(ref), ref, alt))
                if len(variation) > 0:
                    sorted_variation = sorted(variation, key=lambda x: x[0])
                    for ix, item in enumerate(sorted_variation):
                        if ix != 0:
                            if item[0] < sorted_variation[ix - 1][1]:
                                return SeqOutput(SeqName, None, "overlapping variation")
                    varied_seq = ""
                    if len(sorted_variation) == 1:
                        varied_seq += baseSeq[: item[0]]
                        varied_seq += item[3]
                        varied_seq += baseSeq[item[1] :]
                    else:
                        for ix, item in enumerate(sorted_variation):
                            if ix == 0:
                                varied_seq += baseSeq[: item[0]]
                                varied_seq += item[3]
                            elif ix == len(sorted_variation) - 1:
                                varied_seq += baseSeq[
                                    sorted_variation[ix - 1][1] : item[0]
                                ]
                                varied_seq += item[3]
                                varied_seq += baseSeq[item[1] :]
                            else:
                                varied_seq += baseSeq[
                                    sorted_variation[ix - 1][1] : item[0]
                                ]
                                varied_seq += item[3]
                    # override baseSeq
                    baseSeq = varied_seq
                if baseSeqStrand == "-":
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
            else:
                bSeq = extract_baseseq(sub1)
                baseSeq, baseSeqChr, baseSeqStart, baseSeqStrand, errormsg = (
                    bSeq.Seq,
                    bSeq.Chr,
                    bSeq.Start,
                    bSeq.Strand,
                    bSeq.errormsg,
                )
                if errormsg != "":
                    return SeqOutput(SeqName, None, errormsg)
                if baseSeqStrand == "-":
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
        return SeqOutput(SeqName, output, "")

    outputs = []
    sec0 = filter(bool, text.splitlines())
    for ix, sub0 in enumerate(sec0):
        try:
            SeqName = sub0[
                re.search("<", sub0).start() + 1 : re.search(">", sub0).start()
            ]
            sub0text = sub0[re.search(">", sub0).start() + 1 :]
        except:
            SeqName = "Sequence_" + str(ix)
            sub0text = sub0
        outputs.append(singleseqstr(SeqName, sub0text))
    # tuple of name and actual seq
    return outputs


if __name__ == "__main__":
    config_file_path = os.path.expanduser("~/.seqstr.config")
    GENOME_DIR = get_genome_dir()
    parser = argparse.ArgumentParser(description="seqstr")
    parser.add_argument("input_file", help="Specify the input file")
    parser.add_argument("--download", help="Specify the genome files to download")
    parser.add_argument(
        "--dir", help="Specify the directory for downloading genome files"
    )
    parser.add_argument("--output", help="Specify the output fasta file path and name")
    args = parser.parse_args()
    try:
        if args.dir:
            GENOME_DIR = args.dir

        if args.download and not args.dir:
            GENOME_DIR = input(
                "Please enter the directory for downloading genome files: "
            )

        if not os.path.exists(GENOME_DIR):
            os.makedirs(GENOME_DIR)

        if args.download:
            par = args.download
            if os.path.exists(GENOME_DIR + par + ".fa"):
                print("genome file already exists")
                if os.path.exists(GENOME_DIR + par + ".fa.fai"):
                    print("genome file index has already been built")
                else:
                    print(
                        "genome file index has not been built yet, it may take more time to extract sequence"
                    )
            else:
                download(par)
        else:
            par = False

        new_line = "GENOME_DIR=" + GENOME_DIR

        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as file:
                lines = file.readlines()

            modified = False
            for i, line in enumerate(lines):
                if line.startswith("GENOME_DIR="):
                    lines[i] = new_line + "\n"
                    modified = True
                    break
            if modified:
                pass
            else:
                lines.append(new_line + "\n")
            with open(config_file_path, "w") as file:
                file.writelines(lines)
        else:
            with open(config_file_path, "w") as file:
                file.write(new_line)
        if args.input_file:
            with open(args.input_file, "r") as file:
                contents = file.read()
                seqstrout = seqstr(contents)
                if args.output:
                    to_fasta(seqstrout, args.output)
                else:
                    to_fasta(seqstrout, args.input_file+".fasta")
    except:
        par = False
        parser.print_help()
