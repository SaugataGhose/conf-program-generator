# AFFILCLEAN.PY
# Author: Saugata Ghose (ghose at illinois dot edu)
# Last Updated: March 26, 2023
#
# script to standardize author affiliations
# for use with gensched.py

affiliation_changes = {
        'UC Berkeley': 'Univ. of California, Berkeley',
        'Berkeley': 'Univ. of California, Berkeley',
        'UCSB': 'Univ. of California, Santa Barbara',
        'UC Santa Barbara': 'Univ. of California, Santa Barbara',
        'UC Santa Cruz': 'Univ. of California, Santa Cruz',
        'UCSC': 'Univ. of California, Santa Cruz',
        'UC San Diego': 'Univ. of California, San Diego',
        'UCSD': 'Univ. of California, San Diego',
        'UCLA': 'Univ. of California, Los Angeles',
        'UC Merced': 'Univ. of California, Merced',
        'UC Davis': 'Univ. of California, Davis',
        'UT Austin': 'Univ. of Texas at Austin',
        'MIT': 'Massachusetts Inst. of Technology',
        'ETHZ': 'ETH Zürich',
        'ETH Zurich': 'ETH Zürich',
        'Purdue': 'Purdue Univ.',
        'Princeton': 'Princeton Univ.',
        'Michigan': 'Univ. of Michigan',
        'ICT, CAS': 'Inst. of Computing Tech., Chinese Academy of Sciences',
        'Northwestern': 'Northwestern Univ.',
        'NC State': 'North Carolina State Univ.',
        'Nvidia': 'NVIDIA',
        'University of Illinois at Urbana-Champaign': 'Univ. of Illinois Urbana-Champaign',
        'University of Illinois--Urbana Champaign': 'Univ. of Illinois Urbana-Champaign',
        'University of Illinois': 'Univ. of Illinois Urbana-Champaign',
        'Illinois': 'Univ. of Illinois Urbana-Champaign',
        'UIUC': 'Univ. of Illinois Urbana-Champaign',
        'Harvard': 'Harvard Univ.',
        'Georgia Tech': 'Georgia Inst. of Technology',
        'Duke': 'Duke Univ.',
        'Cornell': 'Cornell Univ.',
        'The University of North Carolina at Chapel Hill': 'Univ. of North Carolina at Chapel Hill',
        'UNC Chapel Hill': 'Univ. of North Carolina at Chapel Hill',
        'UNC': 'Univ. of North Carolina at Chapel Hill',
        'U. Washington': 'Univ. of Washington',
        'Yale': 'Yale Univ.',
        'NYU': 'New York Univ.',
        'KAUST': 'King Abdullah Univ. of Science and Technology',
        'The City University of Hong Kong': 'City Univ. of Hong Kong',
        'UNSW Sydney': 'Univ. of New South Wales, Sydney',
        'CMU': 'Carnegie Mellon Univ.',
        'USC': 'Univ. of South California',
        'Stanford': 'Stanford Univ.',
        'Wisconson': 'Univ. of Wisconsin&ndash;Madison',
        'University of Wisconson': 'Univ. of Wisconsin&ndash;Madison',
        'University of Wisconson-Madison': 'Univ. of Wisconsin&ndash;Madison',
        'UBC': 'Univ. of British Columbia',
        'TU Munich': 'Technische Univ. München',
        'TU Dresden': 'Technische Univ. Dresden',
        'TU Delft': 'Technische Univ. Delft',
        'Delft University of Technology': 'Technische Univ. Delft',
        'MPI-SWS': 'Max Planck Inst. for Software Syst.',
        };

abbreviations = {
        'University': 'Univ.',
        'Universität': 'Univ.',
        'U.': 'Univ.',
        'Institute': 'Inst.',
        'Systems': 'Syst.'
        };


def clean_affil(affil):
    affil = affil.strip();

    if affil in affiliation_changes:
        affil = affiliation_changes[affil];
    else:
        for old, new in abbreviations.items():
            affil = affil.replace(old, new);

    return affil;
