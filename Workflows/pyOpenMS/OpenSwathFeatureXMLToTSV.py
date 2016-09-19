#!/usr/bin/env python
import pyopenms
import csv
import sys

def convert_to_row(first, targ, run_id, keys, filename):
    peptide_ref = first.getMetaValue("PeptideRef")
    pep = targ.getPeptideByRef(peptide_ref)
    full_peptide_name = "NA"
    if (pep.metaValueExists("full_peptide_name")):
      full_peptide_name = pep.getMetaValue("full_peptide_name")

    decoy = "0"
    peptidetransitions = [t for t in targ.getTransitions() if t.getPeptideRef() == peptide_ref]
    if len(peptidetransitions) > 0:
        if peptidetransitions[0].getDecoyTransitionType() == pyopenms.DecoyTransitionType().DECOY:
            decoy = "1"
        elif peptidetransitions[0].getDecoyTransitionType() == pyopenms.DecoyTransitionType().TARGET:
            decoy = "0"

    protein_name = "NA"
    if len(pep.protein_refs) > 0:
      protein_name = pep.protein_refs[0]

    row = [
        first.getMetaValue("PeptideRef"),
        run_id,
        filename,
        first.getRT(),
        first.getUniqueId(),
        pep.sequence,
        full_peptide_name,
        pep.getChargeState(),
        first.getMetaValue("PrecursorMZ"),
        first.getIntensity(),
        protein_name,
        decoy
    ]

    for k in keys:
        row.append(first.getMetaValue(k))

    return row

def get_header(features):
    keys = []
    features[0].getKeys(keys)
    header = [
        "transition_group_id",
        "run_id",
        "filename",
        "RT",
        "id",
        "Sequence" ,
        "FullPeptideName",
        "Charge",
        "m/z",
        "Intensity",
        "ProteinName",
        "decoy"]
    header.extend(keys)
    return header

def main(options):

    # load featureXML
    features = pyopenms.FeatureMap()
    fh = pyopenms.FileHandler()
    fh.loadFeatures(options.infile, features)

    # load TraML file
    targeted = pyopenms.TargetedExperiment();
    tramlfile = pyopenms.TraMLFile();
    tramlfile.load(options.traml_in, targeted);

    # write TSV file
    filename = options.infile.split(".")[0]
    fh = open(options.outfile, "w")
    wr = csv.writer(fh, delimiter='\t')
    header = get_header(features)
    wr.writerow(header)
    for f in features:
        keys = []
        f.getKeys(keys)
        row = convert_to_row(f,targeted,filename,keys,filename)
        wr.writerow(row)

def handle_args():
    import argparse

    usage = "" 
    usage += "\nOpenSwathFeatureXMLToTSV -- Converts a featureXML to a mProphet tsv."

    parser = argparse.ArgumentParser(description = usage )
    parser.add_argument('--in', dest="infile", help = 'An input file containing features [featureXML]')
    parser.add_argument("--tr", dest="traml_in", help="An input file containing the transitions [TraML]")
    parser.add_argument("--out", dest="outfile", help="Output mProphet TSV file [tsv]")

    args = parser.parse_args(sys.argv[1:])
    return args

if __name__ == '__main__':
    options = handle_args()
    main(options)
