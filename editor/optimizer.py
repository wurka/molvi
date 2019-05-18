# оптимизация энергии молекулы


atom_config = {
	atoms: [{
		x: 0,
		y: 0,
		z: 0,
		caption: 'H'
	}
	]
}

class NotImplementedException: Exc

def get_bond_energy():
	raise NotImplementedError ("get_bond_energy")

def get_over_energy():
	raise NotImplementedError("get_over_energy")

def get_under_energy():
	raise NotImplementedError("get_under_energy")

def get_val_energy():
	raise NotImplementedError("get_val_energy")

def get_pen_energy():
	raise NotImplementedError("get_pen_energy")

def get_tors_energy():
	raise NotImplementedError("get_tors_energy")

def get_conj_energy():
	raise NotImplementedError("get_conj_energy")

def get_vdwaals_energy():
	raise NotImplementedError("get_vdwaals_energy")

def get_coulomb_energy():
	raise NotImplementedError("get_coulomb_energy")
	
# получить полную энергию совокупности атомов
def get_energy():
	e_bond = get_bond_energy()
	e_over = get_over_energy()
	e_under = get_under_energy()
	e_val = get_val_energy()
	e_pen = get_pen_energy()
	e_tors = get_tors_energy()
	e_conj = get_conj_energy()
	e_vdwaals = get_vdwaals_energy()
	e_coulomb = get_coulomb_energy()