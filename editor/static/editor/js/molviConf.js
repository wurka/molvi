var MolviConf = {
    AtomColors : {
        "H": 0xffffff,
        "C": 0x707070,
        "N": 0x2233FF,
        "O": 0xFF2200,
        "F": 0x00FF00,
        "Cl": 0x00FF00,
        "Br": 0x992200,
        "I": 0x6600BB,
        "He": 0x00FFFF,
        "Ne": 0x00FFFF,
        "Ar": 0x00FFFF,
        "Xe": 0x00FFFF,
        "Kr": 0x00FFFF,
        "P": 0xFF9900,
        "S": 0xFFE522,
        "B:": 0xFFAA77,
        "Li": 0x7700FF,
        "Na": 0x7700FF,
        "K": 0x7700FF,
        "Rb": 0x7700FF,
        "Cs": 0x7700FF,
        "Be": 0x007700,
        "Mg": 0x007700,
        "Ca": 0x007700,
        "Sr": 0x007700,
        "Ba": 0x007700,
        "Ra": 0x007700,
        "Ti": 0x999999,
        "Fe": 0xDD7700,
        "Other": 0xDD77FF
    },
    getAtomColor : function (atomName) {
        if (MolviConf.AtomColors[atomName] == undefined) {
            return MolviConf.AtomColors["Other"];
        } else {
            return MolviConf.AtomColors[atomName];
        }
    },
    AtomRadius: {
        "H": 0.3,
        "He": 0.93,
        "Li": 1.52,
        "Be": 0.7,
        "B": 0.88,
        "C": 0.77,
        "N": 0.7,
        "O": 0.66,
        "F": 0.64,
        "Ne": 1.12,
        "Na": 1.86,
        "Mg": 1.6,
        "Al": 1.43,
        "Sl": 1.17,
        "P": 1.1,
        "S": 1.04,
        "Cl": 0.99,
        "Ar": 1.54,
        "K": 2.31,
        "Ca": 1.97,
        "Sc": 1.6,
        "Ti": 1.46,
        "V": 1.31,
        "Cr": 1.25,
        "Mn": 1.29,
        "Fe": 1.26,
        "Co": 1.25,
        "Ni": 1.24,
        "Cu": 1.28,
        "Zn": 1.33,
        "Ga": 1.22,
        "Ge": 1.22,
        "As": 1.21,
        "Se": 1.17,
        "Br": 1.14,
        "Kr": 1.69,
        "Rb": 2.44,
        "Sr": 2.15,
        "Y": 1.8,
        "Zr": 1.57,
        "Nb": 1.41,
        "Mo": 1.36,
        "Tc": 1.3,
        "Ru": 1.33,
        "Rh": 1.34,
        "Pd": 1.38,
        "Ag": 1.44,
        "Cd": 1.49,
        "In": 1.62,
        "Sn": 1.4,
        "Sb": 1.41,
        "Te": 1.37,
        "I": 1.33,
        "Xe": 1.9,
        "Cs": 2.62,
        "Ba": 2.17,
        "La": 1.88,
        "Hf": 1.57,
        "Ta": 1.43,
        "W": 1.37,
        "Re": 1.37,
        "Os": 1.34,
        "Ir": 1.35,
        "Pt": 1.38,
        "Au": 1.44,
        "Hg": 1.51,
        "Tl": 1.71,
        "Pb": 1.75,
        "Bi": 1.46,
        "Po": 1.4,
        "At": 1.4,
        "Rn": 2.2,
        "Fr": 2.7,
        "Ra": 2.2,
        "Ac": 2.0,
        "Other": 1.0
    }, 
    getAtomRadius : function(atomName){
        //возвращается радиус атома. Название элемента - atomName
        var factor = 0.5;
        if (MolviConf.AtomRadius[atomName] === undefined){
            return AtomRadius["Other"] * factor;
        } else {
            return MolviConf.AtomRadius[atomName] * factor;
        }

    }
}
