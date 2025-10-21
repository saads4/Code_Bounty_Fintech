from dataclasses import dataclass
from typing import Dict

@dataclass
class TaxResult:
    regime: str
    taxable_income: float
    tax: float
    cess: float
    total: float
    details: Dict[str, float]

def slab_tax_new(income: float)->float:
    slabs = [(0,300000,0.0),(300000,700000,0.05),(700000,1000000,0.10),(1000000,1200000,0.15),(1200000,1500000,0.20),(1500000,10**12,0.30)]
    tax = 0.0
    for a,b,r in slabs:
        if income>a: tax += max(0, min(income,b)-a)*r
    return tax

def slab_tax_old(income: float)->float:
    slabs = [(0,250000,0.0),(250000,500000,0.05),(500000,1000000,0.20),(1000000,10**12,0.30)]
    tax = 0.0
    for a,b,r in slabs:
        if income>a: tax += max(0, min(income,b)-a)*r
    return tax

def compute_tax(income: float, deductions: float=0.0, use_new: bool=True)->dict:
    std_ded = 50000.0 if not use_new else 75000.0
    taxable = max(0.0, income - std_ded - (0.0 if use_new else deductions))
    tax = slab_tax_new(taxable) if use_new else slab_tax_old(taxable)
    cess = 0.04*tax; total = tax + cess
    return {"regime":"new" if use_new else "old","taxable_income":taxable,"tax":tax,"cess":cess,"total":total,"details":{"std_deduction":std_ded,"other_deductions":0.0 if use_new else deductions}}

def suggest_deductions_old_regime()->Dict[str, float]:
    return {"80C (PF/ELSS/PPF etc.)":150000, "80D (Health Insurance)":25000, "HRA (rent)":0, "Home Loan Interest (Sec 24)":200000}
