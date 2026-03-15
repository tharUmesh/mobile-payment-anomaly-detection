#!/usr/bin/env python3
import sys

def run_mapper():
    # Read line by line from standard input
    for line in sys.stdin:
        # Strip leading/trailing whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Split the CSV line
        parts = line.split(',')
        
        # Skip the header row
        if parts[0] == 'step':
            continue
            
        # Ensure the row has the correct number of columns (PaySim has 11)
        if len(parts) == 11:
            try:
                # Extract the expanded necessary fields
                step = parts[0]
                tx_type = parts[1]
                amount = parts[2]
                nameOrig = parts[3]
                oldbalanceOrg = parts[4]  # NEW: Balance before tx
                newbalanceOrig = parts[5]
                nameDest = parts[6]
                oldbalanceDest = parts[7] # NEW: Dest balance before
                newbalanceDest = parts[8] # NEW: Dest balance after
                
                # Output 8 data points in the value string
                print(f"{nameOrig}\t{step},{tx_type},{amount},{oldbalanceOrg},{newbalanceOrig},{nameDest},{oldbalanceDest},{newbalanceDest}")
                
            except IndexError:
                continue

if __name__ == "__main__":
    run_mapper()