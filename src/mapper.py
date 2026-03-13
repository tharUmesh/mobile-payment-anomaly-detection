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
        
        # Skip the header row (the first column of the header is 'step')
        if parts[0] == 'step':
            continue
            
        # Ensure the row has the correct number of columns (PaySim has 11)
        if len(parts) == 11:
            try:
                # Extract the necessary fields
                step = parts[0]
                tx_type = parts[1]
                amount = parts[2]
                nameOrig = parts[3]
                newbalanceOrig = parts[5]
                nameDest = parts[6]
                
                # The Key is the origin account (nameOrig)
                # The Value is a comma-separated string of the transaction details
                # Hadoop requires the Key and Value to be separated by a tab (\t)
                print(f"{nameOrig}\t{step},{tx_type},{amount},{newbalanceOrig},{nameDest}")
                
            except IndexError:
                # Silently ignore malformed lines to prevent the job from crashing
                continue

if __name__ == "__main__":
    run_mapper()