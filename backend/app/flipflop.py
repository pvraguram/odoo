from typing import List, Dict
import itertools

class FlipFlopConverter:
    """
    Classical Flip-Flop Converter:
    1. Characteristic table of required FF
    2. Excitation table of available FF
    3. Conversion table
    4. Boolean equations for available FF inputs
    5. Textual circuit description
    """

    valid_ffs = ["D", "T", "JK", "SR"]

    def __init__(self, available_ff: str, required_ff: str):
        self.available_ff = available_ff.upper()
        self.required_ff = required_ff.upper()

        if self.available_ff not in self.valid_ffs or self.required_ff not in self.valid_ffs:
            raise ValueError(f"Flip-flop type must be one of {self.valid_ffs}")

    # --------------------------------
    # Step 2: Characteristic Table
    # --------------------------------
    def characteristic_table(self) -> List[Dict]:
        if self.required_ff == "D":
            return [{"Qn":0,"Input":0,"Qn1":0},
                    {"Qn":0,"Input":1,"Qn1":1},
                    {"Qn":1,"Input":0,"Qn1":0},
                    {"Qn":1,"Input":1,"Qn1":1}]
        elif self.required_ff == "T":
            return [{"Qn":0,"Input":0,"Qn1":0},
                    {"Qn":0,"Input":1,"Qn1":1},
                    {"Qn":1,"Input":0,"Qn1":1},
                    {"Qn":1,"Input":1,"Qn1":0}]
        elif self.required_ff == "JK":
            # 8 rows: Qn, J, K, Qn+1
            table=[]
            for Qn in [0,1]:
                for J in [0,1]:
                    for K in [0,1]:
                        if Qn==0:
                            Qn1 = J
                        else:
                            if K==1: Qn1 = 0
                            else: Qn1 = 1
                        table.append({"Qn":Qn,"J":J,"K":K,"Qn1":Qn1})
            return table
        elif self.required_ff == "SR":
            # SR latch (no invalid check)
            table=[]
            for Qn in [0,1]:
                for S in [0,1]:
                    for R in [0,1]:
                        if S==R==1:
                            Qn1="X"  # invalid
                        elif S==1: Qn1=1
                        elif R==1: Qn1=0
                        else: Qn1=Qn
                        table.append({"Qn":Qn,"S":S,"R":R,"Qn1":Qn1})
            return table

    # --------------------------------
    # Step 3: Excitation Table
    # --------------------------------
    def excitation_table(self) -> List[Dict]:
        if self.available_ff == "D":
            return [{"Qn":0,"Qn1":0,"D":0},
                    {"Qn":0,"Qn1":1,"D":1},
                    {"Qn":1,"Qn1":0,"D":0},
                    {"Qn":1,"Qn1":1,"D":1}]
        elif self.available_ff == "T":
            return [{"Qn":0,"Qn1":0,"T":0},
                    {"Qn":0,"Qn1":1,"T":1},
                    {"Qn":1,"Qn1":0,"T":1},
                    {"Qn":1,"Qn1":1,"T":0}]
        elif self.available_ff == "JK":
            return [{"Qn":0,"Qn1":0,"J":0,"K":"X"},
                    {"Qn":0,"Qn1":1,"J":1,"K":"X"},
                    {"Qn":1,"Qn1":0,"J":"X","K":1},
                    {"Qn":1,"Qn1":1,"J":"X","K":0}]
        elif self.available_ff == "SR":
            return [{"Qn":0,"Qn1":0,"S":0,"R":0},
                    {"Qn":0,"Qn1":1,"S":1,"R":0},
                    {"Qn":1,"Qn1":0,"S":0,"R":1},
                    {"Qn":1,"Qn1":1,"S":0,"R":0}]

    # --------------------------------
    # Step 4: Generate Conversion Table
    # --------------------------------
    def generate_conversion_table(self, truth_table: List[Dict]) -> List[Dict]:
        """
        truth_table: [{"Qn":0,"Next":1,...inputs...}]
        Returns conversion table with available FF inputs
        """
        conv_table=[]
        excitation_map = self.excitation_table()
        for row in truth_table:
            ps = row["Qn"]
            ns = row["Next"]
            # map to available FF inputs
            match = next((ex for ex in excitation_map if ex["Qn"]==ps and ex["Qn1"]==ns),None)
            if match:
                combined={**row,**{k:v for k,v in match.items() if k not in ["Qn","Qn1"]}}
                conv_table.append(combined)
        return conv_table

    # --------------------------------
    # Step 5: Derive Boolean Expressions
    # --------------------------------
    def derive_boolean_expressions(self, conversion_table: List[Dict]) -> Dict[str,str]:
        """
        Very basic SOP (sum-of-products) generation for available FF inputs
        """
        if not conversion_table:
            return {}
        # find all signal names except Qn, Next
        input_names=[k for k in conversion_table[0].keys() if k not in ["Qn","Next"]]
        ff_inputs=[k for k in input_names if k not in ["X"]]  # all columns except don't cares
        results={}
        for ff_inp in ff_inputs:
            terms=[]
            for row in conversion_table:
                val=row.get(ff_inp)
                if val in [1,True]:
                    # product term for all other vars
                    literals=[]
                    for var in input_names:
                        if var==ff_inp: continue
                        bit=row[var]
                        if bit in [0,False]:
                            literals.append(f"~{var}")
                        elif bit in [1,True]:
                            literals.append(f"{var}")
                    terms.append("*".join(literals) if literals else "1")
            results[ff_inp]=" + ".join(terms) if terms else "0"
        return results

    # --------------------------------
    # Step 6: Generate Circuit Description
    # --------------------------------
    def generate_circuit_description(self, equations: Dict[str,str]) -> str:
        lines=[f"{inp} = {eq}" for inp,eq in equations.items()]
        lines.append(f"Connect outputs to {self.available_ff} flip-flop inputs.")
        lines.append(f"Q output is the required {self.required_ff} flip-flop behavior.")
        return "\n".join(lines)

    # --------------------------------
    # Full Pipeline
    # --------------------------------
    def convert(self, truth_table: List[Dict]) -> Dict:
        char_table=self.characteristic_table()
        exc_table=self.excitation_table()
        conv_table=self.generate_conversion_table(truth_table)
        eqs=self.derive_boolean_expressions(conv_table)
        circuit=self.generate_circuit_description(eqs)
        return {
            "characteristic_table": char_table,
            "excitation_table": exc_table,
            "conversion_table": conv_table,
            "boolean_equations": eqs,
            "circuit_description": circuit
        }
