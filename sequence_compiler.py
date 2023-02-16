import re
import numpy as np
import selene_sdk

def toSeq(text):
    text = text.strip()

    if ':' in text:#[genome]chr:start-end strand
        geno = re.sub('[^0-9a-zA-Z]','', text[re.search('\[', text).start()+1:re.search('\]', text).start()])    
        
        #define genome here
        genome = selene_sdk.sequences.Genome(
                                input_path='/archive/bioinformatics/Zhou_lab/shared/jzhou/GraphSeq/Homo_sapiens.GRCh38.dna.primary_assembly.fa',
                                blacklist_regions= 'hg38'
                        )
        sub = text[re.search('\]', text).start()+1:].split(':')
        chr = re.sub('[^0-9a-zA-Z]','', sub[0])
        ps = sub[1]
        
        position = re.sub('[^0-9-]','',ps[re.search('\d', ps).start():-re.search('\d', ps[::-1]).start()])
        start = int(position.split('-')[0])
        end = int(position.split('-')[1])
        strand = re.sub('[^+-]','',ps[-re.search('\d', ps[::-1]).start():])

        seq = genome.get_sequence_from_coords(chr, start, end, '+')
        return seq,chr,start,strand
    else:
        return re.sub('[^atcgnATCGN]','',text).upper(),None,None,None

def reverse_seq(seq):
    rev_seq = ''
    dct =  {'A': 'T', 'C': 'G', 'G': 'C', 'N': 'N', 'T': 'A', 'a': 'T', 'c': 'G', 'g': 'C', 'n': 'N', 't': 'A'}
    for item in seq:
        if item in dct.keys():
            rev_seq += dct[item]
        else:
            rev_seq += item
    return rev_seq[::-1]

def parser(text):
    #sec for arr, sub for string
    #each section ends with ;
    #, for continuation 
    #@chr mutpos ref alt
    
    output = ''
    sec1 = filter(bool, text.split(';'))
    for sub1 in sec1:
   
        sub1 = re.sub(' +', ' ', sub1)#remove extra spaces
        if ',' in sub1:
            sec2 = sub1.split(',')
            baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand = toSeq(sec2[0])#base seq
            
          
            for sub2 in sec2:
                if '@' in sub2:
                    sub2 = ' '.join(sub2[re.search('[chr*]', sub2).span()[0]:].split(' ')[1:])
                    sec3 = re.sub(' +', ' ',re.sub('[^atcgnATCGN ]','',sub2[-re.search('\d', sub2[::-1]).start():].lstrip())).split(' ')
                    
                    mutpos = int(re.sub('[^0-9]','',sub2[re.search('\d', sub2).start():-re.search('\d', sub2[::-1]).start()]))
                    ref = re.sub('[^a-zA-Z]','',sec3[0]).upper()
                    alt = re.sub('[^a-zA-Z]','',sec3[1]).upper()
                 
                    baseSeq = baseSeq[:(mutpos-baseSeqStart)] + alt + baseSeq[(mutpos-baseSeqStart+len(ref)):]
            
            if baseSeqStrand == '-':
                baseSeq = reverse_seq(baseSeq)
            output += baseSeq
        else:
            if ':' in sub1:
                baseSeq,baseSeqChr,baseSeqStart,baseSeqStrand = toSeq(sub1)
                if baseSeqStrand == '-':
                    baseSeq = reverse_seq(baseSeq)
            else:
                baseSeq = re.sub('[^atcgnATCGN]','',sub1).upper()
            output += baseSeq
                
    return output,baseSeqChr,baseSeqStart       
        
