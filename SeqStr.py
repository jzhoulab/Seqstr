import selene_sdk
import re
import os
PROJECT_DIR = os.environ['PROJECT_PATH']

def reverse_seq(seq):
    rev_seq = ''
    dct =  {'A': 'T', 'C': 'G', 'G': 'C', 'N': 'N', 'T': 'A', 'a': 'T', 'c': 'G', 'g': 'C', 'n': 'N', 't': 'A'}
    for item in seq:
        if item in dct.keys():
            rev_seq += dct[item]
        else:
            rev_seq += item
    return rev_seq[::-1]
def toSeq(text):
    text =  text.strip()

    if ':' in text:#chr:start-end strand
        try:
            geno = text[re.search('\[', text).start()+1:re.search('\]', text).start()]    
        except:
            geno = 'hg38'
        #define genome input path using dict map
        genome = selene_sdk.sequences.Genome(
                                input_path=PROJECT_DIR+'/Homo_sapiens.GRCh38.dna.primary_assembly.fa',
                                blacklist_regions= 'hg38'
                            )
        sub = text[re.search('\]', text).start()+1:].split(':')
        chr = sub[0]
        position = sub[1].split(' ')[0].replace(' ', '')
        start = int(position.split('-')[0])
        end = int(position.split('-')[1])
        strand = sub[1].split(' ')[1]
        
        seq = genome.get_sequence_from_coords(chr, start, end, '+')
        return seq,chr,start,strand
    else:
        return text.upper(),None,None,None
    

def parser(text):
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
        sub0text = re.sub(' +', ' ', sub0text)#remove extra spaces
        sec1 = sub0text.split(';')
        for sub1 in sec1:
            sub1 = re.sub(' +', ' ', sub1)#remove extra spaces
            if ',' in sub1:
                sec2 = sub1.split(',')
                baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand = toSeq(sec2[0])#base seq
                variation = []
                for sub2 in sec2:
                    if '@' in sub2:#check overlap then chop by affected region                        
                        sec3 = sub2.split(' ')
                        mutpos = int(sec3[1])-baseSeqStart
                        ref = sec3[2].upper()
                        alt = sec3[3].upper()
                        variation.append((mutpos,mutpos+len(ref),ref,alt))    
                if len(variation) > 0:
                    sorted_variation = sorted(variation, key=lambda x: x[0])
                    for ix,item in enumerate(sorted_variation):
                        if ix != 0:
                            if item[0] < sorted_variation[ix-1][1]:
                                print("overlapping variation")
                                return None
                    varied_seq = ''
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
                    baseSeq = varied_seq#copy to baseSeq
                if baseSeqStrand == '-':
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
            else:
                baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand = toSeq(sub1)
                if baseSeqStrand == '-':
                    baseSeq = reverse_seq(baseSeq)
                output += baseSeq
            outputs.append((SeqName, output)) 
    return outputs#tuple of name and actual seq