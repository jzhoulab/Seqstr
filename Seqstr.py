import selene_sdk
import re
import requests
import sys
import os
import subprocess


def get_genome_dir():
    config_file_path = '~/.seqstr.config'
    if os.path.isfile(config_file_path):
        with open(config_file_path, "r") as config_file:
            for line in config_file:
                if line.startswith("GENOME_DIR="):
                    GENOME_DIR = line.split("=")[1].strip()
                    break
    else:
        GENOME_DIR = "./"

    return GENOME_DIR

def download(par):
    url = 'https://hgdownload.soe.ucsc.edu/goldenPath/'+par+'/bigZips/'+par+'.fa.gz'
    output_file = par+'.fa.gz'
    # Download the file using wget
    download_command = ['wget', url, '-O', output_file]
    try:
        subprocess.run(download_command, check=True)
        print('Download completed successfully.')
    except subprocess.CalledProcessError as e:
        print('Error:', e)
    # Extract the downloaded file using gunzip
    extract_command = ['gunzip', output_file]
    try:
        subprocess.run(extract_command, check=True)
        print('Extraction completed successfully.')
    except subprocess.CalledProcessError as e:
        print('Error:', e)

def reverse_seq(seq):
    rev_seq = ''
    dct =  {'A': 'T', 'C': 'G', 'G': 'C', 'N': 'N', 'T': 'A', 'a': 'T', 'c': 'G', 'g': 'C', 'n': 'N', 't': 'A'}
    for item in seq:
        if item in dct.keys():
            rev_seq += dct[item]
        else:
            rev_seq += item
    return rev_seq[::-1]

def extract_baseseq(text):
    text =  text.strip()
    #chr:start-end strand
    if ':' in text:
        try:
            geno = text[re.search('\[', text).start()+1:re.search('\]', text).start()]    
            sub = text[re.search('\]', text).start()+1:].split(':')
        except:
            geno = 'hg38'
            sub = text.lstrip().split(':')
        chr = sub[0]
        position = sub[1].split(' ')[0].replace(' ', '')
        try:
            start = int(position.split('-')[0])
            end = int(position.split('-')[1])
        except:
            return None,None,None,None,"invalid coordinate input"
        try:
            strand = sub[1].split(' ')[1]
            if strand not in ['+','-']:
                return None,None,None,None,"invalid strand input"
        except:
            return None,None,None,None,"invalid strand input"
        #define genome input path using dict map
        if os.path.exists(GENOME_DIR+geno+'.fa'):
            genome = selene_sdk.sequences.Genome(
                                input_path=GENOME_DIR+geno+'.fa'
                            )
            try:
                seq = genome.get_sequence_from_coords(chr, start, end, '+')
                if len(seq) < 1:
                    return None,None,None,None,"cannot retrieve sequence"
            except:
                return None,None,None,None,"cannot retrieve sequence"
        else:
            url = 'https://api.genome.ucsc.edu/getData/sequence?'
            params = {
                'genome': geno,
                'chrom': chr,
                'start': start,
                'end': end
            }
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    seq = response.json().get('dna')
                else:
                    print('Error:', response.status_code)
            except requests.RequestException as e:
                print('Error:', e)     
        return seq,chr,start,strand,""
    else:
        return text.upper(),None,None,None,""
    

def seqstr(text):
    #sec for arr, sub for string
    #each section ends with ;
    #, for continuation 
    #@chr mutpos ref alt
    #\n for multiple sequences 
    outputs = []
    sec0 = filter(bool, text.splitlines())
    for ix, sub0 in enumerate(sec0):
        try:
            SeqName = sub0[re.search('<', sub0).start()+1:re.search('>', sub0).start()]
            sub0text = sub0[re.search('>', sub0).start()+1:] 
        except:
            SeqName = "Sequence " + str(ix)
            sub0text = sub0
        output = ''
        #remove extra spaces
        sub0text = re.sub(' +', ' ', sub0text)
        sec1 = sub0text.split(';')
        for sub1 in sec1:
            #remove extra spaces
            sub1 = re.sub(' +', ' ', sub1)
            if ',' in sub1:
                sec2 = sub1.split(',')
                #base seq
                baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand,errormsg = extract_baseseq(sec2[0])
                if errormsg != "":
                    return None,errormsg
                variation = []
                for sub2 in sec2:
                    #check overlap then chop by affected region
                    if '@' in sub2:                        
                        sec3 = sub2[re.search('@', sub2).start()+1:].split(' ')
                        try:
                            mutpos = int(sec3[1])-baseSeqStart
                        except:
                            return None,"invalid variant coordinate"
                        try:
                            ref = sec3[2].upper()
                            alt = sec3[3].upper()
                        except:
                            return None,"invalid reference/alternative allele"
                        variation.append((mutpos,mutpos+len(ref),ref,alt))    
                if len(variation) > 0:
                    sorted_variation = sorted(variation, key=lambda x: x[0])
                    for ix,item in enumerate(sorted_variation):
                        if ix != 0:
                            if item[0] < sorted_variation[ix-1][1]:
                                return None,"overlapping variation"
                    varied_seq = ''
                    if len(sorted_variation) == 1:
                        varied_seq += baseSeq[:item[0]]
                        varied_seq += item[3]
                        varied_seq += baseSeq[item[1]:]
                    else:  
                        for ix,item in enumerate(sorted_variation):
                            if ix == 0:
                                varied_seq += baseSeq[:item[0]]
                                varied_seq += item[3]
                            elif ix == len(sorted_variation)-1:
                                varied_seq += baseSeq[sorted_variation[ix-1][1]:item[0]]
                                varied_seq += item[3]
                                varied_seq += baseSeq[item[1]:]
                            else:
                                varied_seq += baseSeq[sorted_variation[ix-1][1]:item[0]]
                                varied_seq += item[3]
                    #override baseSeq
                    baseSeq = varied_seq
                if baseSeqStrand == '-':
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
            else:
                baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand,errormsg = extract_baseseq(sub1)
                if errormsg != "":
                    return None,errormsg
                if baseSeqStrand == '-':
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
        outputs.append((SeqName, output)) 
    #tuple of name and actual seq
    return outputs,""
if __name__ == "__main__":
    # python seqstr.py --download=hg38
    # GENOME_DIR = os.environ['GENOME_DIR']
    GENOME_DIR = get_genome_dir()
    cmd = ''
    try:
        for arg in sys.argv:
            if arg.startswith("--download="):
                par = arg.split("=")[1]
                cmd = 'download'
            elif arg.startswith("--dir="):
                GENOME_DIR = arg.split("=")[1]

        if cmd == 'download':
            if os.path.exists(GENOME_DIR+par+'.fa'):
                print('genome file already exists')
                if os.path.exists(GENOME_DIR+par+'.fa.fai'):
                    print('genome file index has already been built')
                else:
                    print('genome file index has not been built yet, it may take more time to extract sequence')
            else:
                download(par)
        else:
            par = False
    except:
        par = False
    print(seqstr("<mouse>[rn7]chr7:5480600-5480620 +\n<human>[hg38]chr7:5480600-5480620 +"))